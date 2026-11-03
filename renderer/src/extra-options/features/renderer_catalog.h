#pragma once
#include "support.h"
void renderer_catalog_poll(void);
void renderer_catalog_database_tick(void *database);
unsigned renderer_catalog_target(void);
int renderer_catalog_focused(void);
void renderer_catalog_focus(unsigned index);
unsigned renderer_catalog_index(void);
void renderer_catalog_confirm(void);
void renderer_catalog_fail(unsigned code);
int renderer_catalog_view_tick(void *page,unsigned char *image);
void renderer_catalog_view_loaded(void);
int renderer_refresh_resolve_model(void *database,const char *media,unsigned *id);
