#include "renderer_boot.h"
#include "logging.h"
static int configured,lean;static ULONGLONG began;
static volatile LONG world_chunks,home_chunks,reported;
int renderer_boot_lean(void){
 if(!configured){
  configured=1;began=GetTickCount64();wchar_t path[1024];DWORD n=GetModuleFileNameW(NULL,path,1024);
  if(n&&n<850){while(n&&path[n-1]!=L'\\')--n;path[n]=0;lstrcatW(path,L"refresh\\leanboot.enabled");lean=GetFileAttributesW(path)!=INVALID_FILE_ATTRIBUTES;}
  log_append(lean?"RENDERER_BOOT: lean bootstrap experiment enabled.\r\n":"RENDERER_BOOT: normal bootstrap measurement enabled.\r\n");
 }
 return lean;
}
void renderer_boot_asset_lookup(const char *name,size_t length,int found){
 if(!found||length>1023||!name||InterlockedCompareExchange(&reported,0,0))return;
 char normalized[1024];for(size_t i=0;i<length;++i){char c=name[i];normalized[i]=(c>='A'&&c<='Z')?(char)(c+32):(c=='\\'?'/':c);}normalized[length]=0;
 if(!text_find(normalized,length,"geochunk"))return;
 volatile LONG *count=text_find(normalized,length,"tracks/anthem/")?&world_chunks:text_find(normalized,length,"tracks/homespace02/")?&home_chunks:NULL;
 if(count){LONG n=InterlockedIncrement(count);if(n<=3){log_append("RENDERER_BOOT: geometry lookup ");log_append(normalized);log_append("\r\n");}}
}
void renderer_boot_view_loaded(void){
 if(InterlockedExchange(&reported,1))return;renderer_boot_lean();
 log_append_value("RENDERER_BOOT: first car view elapsed ms=",(int)(GetTickCount64()-began));
 log_append_value("RENDERER_BOOT: mainland geometry lookups=",(int)InterlockedCompareExchange(&world_chunks,0,0));
 log_append_value("RENDERER_BOOT: homespace geometry lookups=",(int)InterlockedCompareExchange(&home_chunks,0,0));
}
