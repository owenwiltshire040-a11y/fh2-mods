#pragma once
#include "support.h"
int renderer_boot_lean(void);
void renderer_boot_asset_lookup(const char *name,size_t length,int found);
void renderer_boot_view_loaded(void);
