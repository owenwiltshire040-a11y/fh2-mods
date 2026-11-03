#include "renderer_camera.h"
#include "logging.h"
#pragma pack(push,1)
typedef struct{char magic[8];unsigned version,serial,command,view;char reserved[40];} Request;
typedef struct{char magic[8];unsigned version,serial,code,view;float fov,pitch,yaw;unsigned outer,inner;float orbit[9];char reserved[48];} Answer;
#pragma pack(pop)
_Static_assert(sizeof(Request)==64 && sizeof(Answer)==128,"camera protocol");
static wchar_t directory[1024];static unsigned serial;static ULONGLONG poll_at,expires;
static void *held_camera,*held_inner;static int owns_orbit;static float original[9],wanted[9];
static void root(void){if(directory[0])return;DWORD n=GetModuleFileNameW(NULL,directory,1024);if(!n||n>850){directory[0]=0;return;}while(n&&directory[n-1]!=L'\\')--n;directory[n]=0;lstrcatW(directory,L"refresh\\");}
static void path(wchar_t out[1024],const wchar_t *name){lstrcpyW(out,directory);lstrcatW(out,name);}
static void apply(unsigned char *image,void *camera,const float values[9]){
 /* CUICarTargetCamera's native orbit state is two vectors at +0x90/+0xa0
    and a FOV at +0xb0. Its own recompute routine frames the current car. */
 memory_copy((unsigned char *)camera+0x90,values,36);
 ((void (*)(void *))(image+0xa99310))(camera);
}
static void answer(const Request *request,unsigned code,unsigned char *image,void *camera,void *inner){
 Answer a={{0},1,request->serial,code,request->view,0,0,0,0,0,{0},{0}};memory_copy(a.magic,"FH2CACK",7);
 if(camera)a.outer=(unsigned)((uintptr_t)*(void **)camera-(uintptr_t)image);
 if(inner){a.inner=(unsigned)((uintptr_t)*(void **)inner-(uintptr_t)image);memory_read((unsigned char *)inner+0x1b0,&a.fov,4);memory_read((unsigned char *)camera+0x94,&a.pitch,4);memory_read((unsigned char *)camera+0x90,&a.yaw,4);memory_read((unsigned char *)camera+0x90,a.orbit,36);}
 static wchar_t tmp[1024],out[1024];path(tmp,L"camera-ack.tmp");path(out,L"camera-ack.bin");DWORD written=0;
 HANDLE file=CreateFileW(tmp,GENERIC_WRITE,0,NULL,CREATE_ALWAYS,FILE_ATTRIBUTE_NORMAL,NULL);if(file==INVALID_HANDLE_VALUE)return;
 int ok=WriteFile(file,&a,sizeof(a),&written,NULL)&&written==sizeof(a);CloseHandle(file);if(ok)MoveFileExW(tmp,out,MOVEFILE_REPLACE_EXISTING|MOVEFILE_WRITE_THROUGH);
}
void renderer_camera_tick(void *page,unsigned char *image){
 void *manager=NULL,*camera=NULL,*inner=NULL,*vt=NULL;
 if(memory_read_pointer(image+0x34e4588,&manager)&&manager)memory_read_pointer((unsigned char *)manager+8,&camera);
 int valid=camera&&memory_read_pointer(camera,&vt)&&vt==image+0x2d50700 &&
  memory_read_pointer((unsigned char *)camera+0x78,&inner)&&inner&&memory_read_pointer(inner,&vt)&&vt==image+0x2d50360;
 ULONGLONG now=GetTickCount64();
 if(owns_orbit&&now>=expires){
  if(valid&&held_camera==camera&&held_inner==inner)apply(image,camera,original);
  held_camera=held_inner=NULL;if(*((unsigned char *)page+0x410))((void (*)(void *))(image+0xcd98b0))(page);owns_orbit=0;
  log_append("RENDERER_CAMERA: timed-out camera mode restored.\r\n");return;
 }
 if(held_camera){
  if(!valid||held_camera!=camera||held_inner!=inner){held_camera=held_inner=NULL;}
  else if(now>=expires){apply(image,camera,original);held_camera=held_inner=NULL;log_append("RENDERER_CAMERA: timed-out capture camera restored.\r\n");}
  else apply(image,camera,wanted);
 }
 if(now<poll_at)return;poll_at=now+100;root();if(!directory[0])return;
 wchar_t name[1024];path(name,L"camera.bin");HANDLE f=CreateFileW(name,GENERIC_READ,FILE_SHARE_READ|FILE_SHARE_DELETE,NULL,OPEN_EXISTING,FILE_ATTRIBUTE_NORMAL,NULL);if(f==INVALID_HANDLE_VALUE)return;
 Request r;DWORD n=0;int ok=ReadFile(f,&r,sizeof(r),&n,NULL);CloseHandle(f);
 if(!ok||n!=sizeof(r)||!memory_equal(r.magic,"FH2CAM1",8)||r.version!=1||r.serial<=serial)return;
 serial=r.serial;if(r.command>3||r.view>6){answer(&r,11,image,NULL,NULL);return;}
 if(r.command==3){
  static const unsigned char code[]={0x40,0x53,0x57,0x48,0x83,0xec,0x38};
  if(!memory_equal(image+0xcd98b0,code,sizeof(code))){log_append("RENDERER_CAMERA: native Change Camera code guard rejected.\r\n");answer(&r,13,image,page,NULL);return;}
  expires=now+25000;if(!*((unsigned char *)page+0x410)){owns_orbit=1;((void (*)(void *))(image+0xcd98b0))(page);}
  answer(&r,3,image,NULL,NULL);return;
 }
 if(r.command==2){
  if(valid&&held_camera==camera){apply(image,camera,original);held_camera=held_inner=NULL;}
  if(owns_orbit&&*((unsigned char *)page+0x410)){((void (*)(void *))(image+0xcd98b0))(page);}
  owns_orbit=0;answer(&r,2,image,NULL,NULL);return;
 }
 if(!valid){answer(&r,10,image,camera,NULL);return;}
 if(r.command==0){answer(&r,1,image,camera,inner);return;}
 if(!held_camera){
  memory_read((unsigned char *)camera+0x90,original,36);
  for(unsigned i=0;i<9;++i)if(!float_is_finite(original[i])){answer(&r,12,image,camera,inner);return;}
  if(original[8]<10.0f||original[8]>120.0f){answer(&r,12,image,camera,inner);return;}
  held_camera=camera;held_inner=inner;
 }
 static const float yaw[]={0.0f,0.0f,1.5707963268f,3.1415926536f,-1.5707963268f,-0.7853981634f,2.3561944902f};
 memory_copy(wanted,original,36);wanted[0]=yaw[r.view];wanted[6]*=1.6f;expires=now+25000;apply(image,camera,wanted);answer(&r,1,image,camera,inner);
}

void renderer_camera_reset(void){held_camera=held_inner=NULL;expires=0;owns_orbit=0;}
