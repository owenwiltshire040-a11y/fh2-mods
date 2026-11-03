#pragma once
#include "support.h"
void renderer_refresh_ui(void *page, unsigned char *image);
void renderer_refresh_view_loaded(void);
void renderer_refresh_database_tick(void *database);
int renderer_mount_revision(const wchar_t *physical,const wchar_t *relative,unsigned addon);
void renderer_refresh_asset_lookup(const char *name,size_t length,int found);
