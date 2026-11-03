#include "renderer_startup.h"
#include "autodrive_game.h"
#include "logging.h"
/* Private viewer only. Dispatch native window-layer input on the existing UI
   update thread; never synthesize desktop input or change startup state flow. */
typedef unsigned char (*MenuKey)(void *,unsigned char,unsigned,unsigned,unsigned char,unsigned char);
static int configured,enabled,continued,pause_sent,finished;
static volatile LONG pause_pending;
static ULONGLONG scene_since,ready_since,deadline;
static char previous[128];
static void release(void *object,unsigned char *image){
 if(object && InterlockedDecrement((volatile LONG *)((unsigned char *)object+0x10))==0)((void (*)(void *))(image+0x257730))(object);
}
static int type_name(void *object,unsigned char *image,char out[128]){
 void *vtable=NULL;uintptr_t locator=0;unsigned type=0;
 if(!memory_read_pointer(object,&vtable)||(uintptr_t)vtable<(uintptr_t)image+0x1dcc000||(uintptr_t)vtable>(uintptr_t)image+0x3400000 ||
    !memory_read((unsigned char *)vtable-8,&locator,8)||locator<(uintptr_t)image+0x1dcc000||locator>(uintptr_t)image+0x3400000 ||
    !memory_read((void *)(locator+12),&type,4)||type<0x1dcc000||type>0x3400000)return 0;
 for(unsigned i=0;i<127;++i){if(!memory_read(image+type+16+i,out+i,1))return 0;if(!out[i])return 1;}out[127]=0;return 0;
}
static void configure(void){
 configured=1;wchar_t path[1024];DWORD n=GetModuleFileNameW(NULL,path,1024);if(!n||n>850)return;
 while(n&&path[n-1]!=L'\\')--n;path[n]=0;lstrcatW(path,L"refresh\\autostart.enabled");
 enabled=GetFileAttributesW(path)!=INVALID_FILE_ATTRIBUTES;
 deadline=GetTickCount64()+300000;
 log_append(enabled?"RENDERER_STARTUP: native automatic startup armed.\r\n":"RENDERER_STARTUP: manual startup selected.\r\n");
}
static unsigned char key(void *manager,unsigned char *image,unsigned value){
 unsigned char result=((MenuKey)(image+0x1422de0))(manager,0,value,0,0,0);
 ((MenuKey)(image+0x1422de0))(manager,1,value,0,0,0);return result;
}
void renderer_startup_tick(unsigned char *image){
 if(!configured)configure();if(!enabled||finished)return;
 ULONGLONG now=GetTickCount64();if(now>deadline){finished=1;log_append("RENDERER_STARTUP: automatic startup timed out; manual controls remain available.\r\n");return;}
 /* WindowLayerManager is stored by native initialization at 0x1411f2e. */
 void *manager=NULL,*vtable=NULL,*owner=NULL,*page=NULL;
 if(!memory_read_pointer(image+0x3684b88,&manager)||!memory_read_pointer(manager,&vtable)||vtable!=image+0x2ecf920||
    !memory_read_pointer((unsigned char *)manager+0x68,&owner)||!owner)return;
 ((void **(*)(void *,void **))(image+0xb70d30))(owner,&page);if(!page)return;
 char name[128];if(!type_name(page,image,name)){release(page,image);return;}
 if(!text_equal_ignore_case(name,previous)){
  memory_copy(previous,name,text_length(name)+1);scene_since=now;
  log_append("RENDERER_STARTUP: active scene ");log_append(name);log_append("\r\n");
 }
 /* Splash registers AVUI key 0x12 at native 0xe8f9a5. Native Windows
    Space maps to that key and runs the actual LoadingState/sign-in action. */
 if(!continued && text_equal_ignore_case(name,".?AVSplash@@") && now-scene_since>=2000){
  continued=1;log_append_value("RENDERER_STARTUP: title Continue binding accepted=",key(manager,image,0x20));
 }
 void *controller=NULL;unsigned short buttons=0;
 int ready=text_equal_ignore_case(name,".?AVHud@@") && now-scene_since>=2000 && autodrive_game_buttons(&controller,&buttons)==0 && autodrive_game_can_start(controller) && autodrive_game_can_drive(controller) && !autodrive_game_is_carmeet();
 if(!ready)ready_since=0;else if(!ready_since)ready_since=now;
 if(!ready)InterlockedExchange(&pause_pending,0);
 if(!pause_sent && ready_since && now-ready_since>=2000){
  if(!InterlockedExchange(&pause_pending,1))log_append("RENDERER_STARTUP: HUD and driving ready; waiting for native Pause entry.\r\n");
 }
 if(pause_sent && (text_find(name,text_length(name),"CarSelect")||text_find(name,text_length(name),"CarView"))){
  finished=1;log_append("RENDERER_STARTUP: native viewer reached automatically.\r\n");
 }
 release(page,image);
}

/* Runs inside WaitForPause's own update callback. The native Pause action
   (input action 0x86) dispatches precisely this transition at self+0x28.
   Retain the game's pause-block counter and state-exit checks. */
void renderer_startup_pause_update(void *behavior,unsigned char *image){
 int blocked=1;
 if(InterlockedCompareExchange(&pause_pending,0,0) && enabled && !finished && !pause_sent &&
    memory_read(image+0x2cf73f0,&blocked,4) && blocked<=0 &&
    !((unsigned char (*)(void *))(image+0x19281b0))(behavior)){
  InterlockedExchange(&pause_pending,0);pause_sent=1;
  log_append("RENDERER_STARTUP: native onPause transition requested.\r\n");
  ((void (*)(void *,void *))(image+0x1925260))(behavior,(unsigned char *)behavior+0x28);return;
 }
 ((void (*)(void *))(image+0x964810))(behavior);
}
