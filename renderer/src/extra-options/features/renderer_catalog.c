#include "renderer_catalog.h"
#include "logging.h"
#pragma pack(push,1)
typedef struct{char magic[8];uint32_t version,serial,car_id;char media[19],reserved[25];} Selection;
typedef struct{char magic[8];uint32_t version,serial,code,car_id;char media[19],reserved[21];} Answer;
#pragma pack(pop)
_Static_assert(sizeof(Selection)==64 && sizeof(Answer)==64,"selection ABI");
static wchar_t directory[1024];static Selection request;static unsigned serial,target,index;
/* 0 idle,1 awaiting DB,2 ready to focus,3 focused,4 confirmed,5 view loaded,-1 rejected */
static volatile LONG state;static ULONGLONG poll_at;static unsigned returned_serial;
static void root(void){
 if(directory[0])return;DWORD n=GetModuleFileNameW(NULL,directory,1024);if(!n||n>850){directory[0]=0;return;}
 while(n && directory[n-1]!=L'\\')--n;directory[n]=0;lstrcatW(directory,L"refresh");
}
static void path(wchar_t out[1024],const wchar_t *name){lstrcpyW(out,directory);lstrcatW(out,L"\\");lstrcatW(out,name);}
static void answer(unsigned code){
 Answer a={{0},1,request.serial,code,target,{0},{0}};memory_copy(a.magic,"FH2SACK",7);memory_copy(a.media,request.media,19);
 static wchar_t tmp[1024],out[1024];path(tmp,L"selection-ack.tmp");path(out,L"selection-ack.bin");DWORD n=0;
 HANDLE f=CreateFileW(tmp,GENERIC_WRITE,0,NULL,CREATE_ALWAYS,FILE_ATTRIBUTE_NORMAL,NULL);if(f==INVALID_HANDLE_VALUE)return;
 int ok=WriteFile(f,&a,sizeof(a),&n,NULL)&&n==sizeof(a);CloseHandle(f);if(ok)MoveFileExW(tmp,out,MOVEFILE_REPLACE_EXISTING|MOVEFILE_WRITE_THROUGH);
}
void renderer_catalog_poll(void){
 LONG s=InterlockedCompareExchange(&state,0,0);if((s>0&&s<5)||GetTickCount64()<poll_at)return;
 poll_at=GetTickCount64()+200;root();if(!directory[0])return;
 wchar_t name[1024];path(name,L"selection.bin");HANDLE f=CreateFileW(name,GENERIC_READ,FILE_SHARE_READ|FILE_SHARE_DELETE,NULL,OPEN_EXISTING,FILE_ATTRIBUTE_NORMAL,NULL);if(f==INVALID_HANDLE_VALUE)return;
 Selection r;DWORD n=0;int ok=ReadFile(f,&r,sizeof(r),&n,NULL);CloseHandle(f);
 if(!ok||n!=sizeof(r)||!memory_equal(r.magic,"FH2SEL1",8)||r.version!=1||r.serial<=serial)return;
 unsigned i=0;for(;i<19&&r.media[i];++i){char c=r.media[i];if(!((c>='A'&&c<='Z')||(c>='a'&&c<='z')||(c>='0'&&c<='9')||c=='_'))return;}
 if(i<3||i>18)return;request=r;serial=r.serial;target=0;InterlockedExchange(&state,1);answer(1);log_append("RENDERER_CATALOG: model selection queued.\r\n");
}
void renderer_catalog_database_tick(void *db){
 if(!db||InterlockedCompareExchange(&state,0,0)!=1)return;
 unsigned id=0;if(!renderer_refresh_resolve_model(db,request.media,&id)){renderer_catalog_fail(10);return;}
 target=id;InterlockedExchange(&state,2);answer(1);log_append_value("RENDERER_CATALOG: resolved installed model ID=",(int)id);
}
unsigned renderer_catalog_target(void){LONG s=InterlockedCompareExchange(&state,0,0);return (s==2||s==3)?target:0;}
int renderer_catalog_focused(void){return InterlockedCompareExchange(&state,0,0)==3;}
void renderer_catalog_focus(unsigned at){index=at;InterlockedExchange(&state,3);answer(2);}
unsigned renderer_catalog_index(void){return index;}
void renderer_catalog_confirm(void){InterlockedExchange(&state,4);answer(3);log_append("RENDERER_CATALOG: native stock-model confirmation requested.\r\n");}
void renderer_catalog_fail(unsigned code){InterlockedExchange(&state,-1);answer(code);log_append_value("RENDERER_CATALOG: selection rejected, code=",(int)code);}
int renderer_catalog_view_tick(void *page,unsigned char *image){
 renderer_catalog_poll();LONG s=InterlockedCompareExchange(&state,0,0);
 if((s==1||s==2) && returned_serial!=serial){
  typedef struct{char text[16];size_t length,capacity;} GameString;const GameString event={"back",4,15};returned_serial=serial;
  ((void (*)(void *,const GameString *))(image+0x1422f10))(page,&event);log_append("RENDERER_CATALOG: returning to native stock picker.\r\n");return 1;
 }
 return s>0&&s<5;
}
void renderer_catalog_view_loaded(void){if(InterlockedCompareExchange(&state,5,4)==4){answer(4);log_append("RENDERER_CATALOG: requested model view initialized.\r\n");}}
