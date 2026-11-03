#include "fh2_plugin.h"
static void (*write_log)(const char *);
static unsigned frames;
static int same(const char *a,const char *b){while(*a&&*a==*b){++a;++b;}return *a==*b;}
static void emit(const char *s){if(write_log)write_log(s);}
BOOL WINAPI DllMain(HINSTANCE h,DWORD reason,LPVOID reserved){(void)h;(void)reason;(void)reserved;return TRUE;}
__declspec(dllexport) BOOL WINAPI FH2PluginInitialize(const FH2PluginContext *c){
 if(!c||c->size<sizeof(*c)||c->api_version!=1||c->adapter!=FH2_PLUGIN_AZIMUTH)return FALSE;
 write_log=c->log_utf8;
 if(c->game_image_size!=60915712u||!c->extra_options_version||!same(c->extra_options_version,"0.3.9")){
  emit("RENDERER_PROBE: rejected incompatible runtime; no game memory changed.\r\n");return FALSE;
 }
 emit("RENDERER_PROBE: initialized; EO 0.3.9; supported image size; observation only.\r\n");return TRUE;
}
__declspec(dllexport) BOOL WINAPI FH2PluginDatabaseUpdate(const FH2PluginDatabaseFrame *f){
 if(!f||f->size<sizeof(*f)||!f->prepare||!f->step||!f->finalize||!f->column_int64)return FALSE;
 void *stmt=0;const char *tail=0;
 if(f->prepare(f->database,"SELECT COUNT(*) FROM Tracks WHERE id=308 AND IsHomespace=1",-1,&stmt,&tail)!=0||!stmt){emit("RENDERER_PROBE: database query unavailable.\r\n");return FALSE;}
 int ok=f->step(stmt)==100&&f->column_int64(stmt,0)==1;f->finalize(stmt);
 emit(ok?"RENDERER_PROBE: merged database ready; homespace 308 verified.\r\n":"RENDERER_PROBE: homespace database check failed.\r\n");return ok;
}
__declspec(dllexport) void WINAPI FH2PluginVehicleUpdate(const FH2PluginVehicleFrame *f){
 if(!f||f->size<sizeof(*f))return;
 if(frames++%600u)return;
 emit(f->car?"RENDERER_PROBE: local-car callback alive.\r\n":"RENDERER_PROBE: callback alive; no local car.\r\n");
 emit(f->input_enabled?"RENDERER_PROBE: gameplay input enabled.\r\n":"RENDERER_PROBE: gameplay input disabled (menu/loading/unfocused).\r\n");
}
