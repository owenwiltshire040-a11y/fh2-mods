#include "renderer_refresh.h"
#include "addon_database.h"
#include "addons.h"
#include "plugins.h"
#include "logging.h"
#pragma pack(push,1)
typedef struct {char magic[8];uint32_t version,serial,car_id;char base[19],media[19],folder[96];char reserved[6];} Request;
typedef struct {char magic[8];uint32_t version,serial,code,car_id;char media[19],reserved[21];} Ack;
#pragma pack(pop)
_Static_assert(sizeof(Request)==160,"request ABI");
_Static_assert(sizeof(Ack)==64,"ack ABI");
typedef struct {char base[19],media[19];unsigned id;} Slot;
static Slot slots[32];static unsigned slot_count,accepted;
static wchar_t directory[1024];static Request request;static unsigned last_serial;
/* 0 idle, 1 queued, 5 processing, 2 applied, 3 reload sent, 4 view reentered, -1 failed. */
static volatile LONG state;
static ULONGLONG next_poll;
static void root(void){
 if(directory[0])return;
 DWORD n=GetModuleFileNameW(NULL,directory,1024);if(!n||n>=850){directory[0]=0;return;}
 while(n && directory[n-1]!=L'\\')--n;directory[n]=0;
 lstrcatW(directory,L"refresh");
}
static void path(wchar_t out[1024],const wchar_t *name){lstrcpyW(out,directory);lstrcatW(out,L"\\");lstrcatW(out,name);}
static int token(const char *s,unsigned capacity,int folder){
 unsigned i=0;for(;i<capacity&&s[i];++i){char c=s[i];if(!((c>='A'&&c<='Z')||(c>='a'&&c<='z')||(c>='0'&&c<='9')||c=='_'||(folder&&(c==' '||c=='-'||c=='('||c==')'))))return 0;}
 return i>0&&i<capacity;
}
static void acknowledge(unsigned code){
 Ack a={{0},1,request.serial,code,request.car_id,{0},{0}};memory_copy(a.magic,"FH2ACK1",7);memory_copy(a.media,request.media,19);
 static wchar_t tmp[1024],out[1024];path(tmp,L"ack.tmp");path(out,L"ack.bin");DWORD written=0;
 HANDLE f=CreateFileW(tmp,GENERIC_WRITE,0,NULL,CREATE_ALWAYS,FILE_ATTRIBUTE_NORMAL,NULL);
 if(f==INVALID_HANDLE_VALUE)return;
 int ok=WriteFile(f,&a,sizeof(a),&written,NULL)&&written==sizeof(a);CloseHandle(f);
 if(ok)MoveFileExW(tmp,out,MOVEFILE_REPLACE_EXISTING|MOVEFILE_WRITE_THROUGH);
}
static char *append(char *p,const char *s){while(*s)*p++=*s++;*p=0;return p;}
static char *number(char *p,unsigned n){char a[12];unsigned k=0;do{a[k++]=(char)('0'+n%10);n/=10;}while(n);while(k)*p++=a[--k];*p=0;return p;}
static int exec(const AddonSqlite *sql,void *db,const char *text){void *s=NULL;if(sql->prepare(db,text,-1,&s,NULL)||!s)return 0;int result=sql->step(s);sql->finalize(s);return result==101;}
static int one_id(const AddonSqlite *sql,void *db,const char *media,unsigned *id){
 char q[160];char *p=append(q,"SELECT Id FROM Data_Car WHERE MediaName='");p=append(p,media);append(p,"'");void *s=NULL;
 if(sql->prepare(db,q,-1,&s,NULL)||!s)return 0;
 int ok=sql->step(s)==100;if(ok){int64_t n=sql->column_int64(s,0);ok=n>0&&n<10000000;if(ok)*id=(unsigned)n;ok=ok&&sql->step(s)==101;}sql->finalize(s);return ok;
}
void renderer_refresh_database_tick(void *db){
 if(!db||InterlockedCompareExchange(&state,5,1)!=1)return;
 const AddonSqlite *sql=addon_database_api();unsigned index=addons_count();
 for(unsigned i=0;i<addons_count();++i){const wchar_t *dir=addons_directory(i);if(!dir||!addons_media_active(i))continue;const wchar_t *base=dir;for(const wchar_t *p=dir;*p;++p)if(*p==L'\\'||*p==L'/')base=p+1;
  wchar_t expected[96];unsigned k=0;for(;request.folder[k];++k)expected[k]=(wchar_t)request.folder[k];expected[k]=0;if(!lstrcmpiW(base,expected)){index=i;break;}}
 Slot *slot=NULL;for(unsigned i=0;i<slot_count;++i)if(text_equal_ignore_case(slots[i].base,request.base)){slot=&slots[i];break;}
 unsigned id=0;const char *old=slot?slot->media:request.base;
 if(index==addons_count()||accepted>=16||(!slot&&slot_count==32)||!one_id(sql,db,old,&id))goto rejected;
 wchar_t file[1024],relative[64];path(file,L"generations\\");unsigned n=(unsigned)lstrlenW(file);for(unsigned i=0;request.media[i];++i)file[n++]=(wchar_t)request.media[i];file[n]=0;lstrcatW(file,L".zip");
 lstrcpyW(relative,L"cars\\");n=(unsigned)lstrlenW(relative);for(unsigned i=0;request.media[i];++i)relative[n++]=(wchar_t)request.media[i];relative[n]=0;lstrcatW(relative,L".zip");
 if(!renderer_mount_revision(file,relative,index)){log_append("RENDERER_REFRESH: fresh archive mount failed.\r\n");acknowledge(12);InterlockedExchange(&state,-1);return;}
 if(!exec(sql,db,"BEGIN IMMEDIATE"))goto database_failed;
 char query[256];char *p=append(query,"UPDATE Data_Car SET MediaName='");p=append(p,request.media);p=append(p,"' WHERE Id=");p=number(p,id);p=append(p," AND MediaName='");p=append(p,old);append(p,"'");
 unsigned check=0;if(!exec(sql,db,query)||!one_id(sql,db,request.media,&check)||check!=id){exec(sql,db,"ROLLBACK");goto database_failed;}
 if(!exec(sql,db,"COMMIT")){exec(sql,db,"ROLLBACK");goto database_failed;}
 if(!slot){slot=&slots[slot_count++];memory_copy(slot->base,request.base,19);}slot->id=id;memory_copy(slot->media,request.media,19);request.car_id=id;++accepted;
 log_append("RENDERER_REFRESH: database switched to ");log_append(request.media);log_append("; original assets retained.\r\n");acknowledge(1);InterlockedExchange(&state,2);return;
 database_failed:log_append("RENDERER_REFRESH: database update refused or rolled back.\r\n");acknowledge(11);InterlockedExchange(&state,-1);return;
 rejected:log_append("RENDERER_REFRESH: request rejected (car, source mod or session limit).\r\n");acknowledge(10);InterlockedExchange(&state,-1);
}
void renderer_refresh_ui(void *page,unsigned char *image){
 plugins_renderer_refresh_ui_tick();
 LONG value=InterlockedCompareExchange(&state,0,0);
 if(value==2){
  /* UI page event is dispatched only on this native UI callback. */
  typedef struct{char data[16];size_t length,capacity;} GameString;
  const GameString event={"_renderer_redo",14,15};
  InterlockedExchange(&state,3);acknowledge(2);
  ((void (*)(void *,const GameString *))(image+0x1422f10))(page,&event);
  log_append("RENDERER_REFRESH: native view reload event sent.\r\n");return;
 }
 if(value==1||value==3||value==5||GetTickCount64()<next_poll)return;
 next_poll=GetTickCount64()+250;root();if(!directory[0])return;
 wchar_t name[1024];path(name,L"request.bin");HANDLE f=CreateFileW(name,GENERIC_READ,FILE_SHARE_READ|FILE_SHARE_DELETE,NULL,OPEN_EXISTING,FILE_ATTRIBUTE_NORMAL,NULL);
 if(f==INVALID_HANDLE_VALUE)return;Request r;DWORD got=0;int ok=ReadFile(f,&r,sizeof(r),&got,NULL);CloseHandle(f);
 if(!ok||got!=sizeof(r)||!memory_equal(r.magic,"FH2RFR1",8)||r.version!=1||!r.serial||r.serial<=last_serial)return;
 last_serial=r.serial;
 if(!token(r.base,19,0)||!token(r.media,19,0)||!token(r.folder,96,1)||text_length(r.base)!=text_length(r.media)||r.media[0]!='R'||r.media[1]!='V'||text_equal_ignore_case(r.base,r.media)){memory_copy(&request,&r,sizeof(r));acknowledge(13);return;}
 memory_copy(&request,&r,sizeof(r));InterlockedExchange(&state,1);log_append("RENDERER_REFRESH: immutable revision queued.\r\n");
}
void renderer_refresh_view_loaded(void){
 if(InterlockedCompareExchange(&state,4,3)==3){acknowledge(3);log_append("RENDERER_REFRESH: new native car-view instance initialized; visual check required.\r\n");}
}

void renderer_refresh_asset_lookup(const char *name,size_t length,int found){
 if(InterlockedCompareExchange(&state,0,0)<2 || !found || length>4096)return;
 static volatile LONG carbin_report,model_report,texture_report;
 const char *hit=text_find(name,length,request.media);
 if(!hit){char lower[19];unsigned i=0;for(;request.media[i];++i){char c=request.media[i];lower[i]=(c>='A'&&c<='Z')?(char)(c+32):c;}lower[i]=0;hit=text_find(name,length,lower);}
 if(!hit)return;
 const char *tag=NULL;
 if(text_find(name,length,".carbin")&&!InterlockedExchange(&carbin_report,1))tag="carbin";
 if(text_find(name,length,".modelbin")&&!InterlockedExchange(&model_report,1))tag="model";
 if(text_find(name,length,".swatchbin")&&!InterlockedExchange(&texture_report,1))tag="texture";
 if(tag){log_append("RENDERER_REFRESH: fresh revision asset resolved: ");log_append(tag);log_append("\r\n");}
}

int renderer_refresh_resolve_model(void *database,const char *media,unsigned *id){
    const AddonSqlite *sql=addon_database_api();
    if(one_id(sql,database,media,id))return 1;
    for(unsigned i=0;i<slot_count;++i)if(text_equal_ignore_case(slots[i].base,media))return one_id(sql,database,slots[i].media,id);
    return 0;
}
