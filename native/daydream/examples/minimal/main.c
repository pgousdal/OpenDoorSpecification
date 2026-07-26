#include "ods_daydream.h"

/*
 * Supply an SDK-specific ods_dd_bindings instance in a separate translation
 * unit. Keeping this file API-neutral is the central portability property.
 */
extern ods_dd_bindings make_daydream_bindings(void);
extern long daydream_launch_node(void);

int main(void) {
    ods_daydream adapter;
    ods_dd_bindings bindings = make_daydream_bindings();
    char name[41];

    if (ods_daydream_init(&adapter, &bindings, daydream_launch_node()) != ODS_DD_OK)
        return 20;
    if (ods_daydream_write(&adapter, "Name: ") != ODS_DD_OK)
        return 20;
    if (ods_daydream_read_line(&adapter, name, sizeof(name)) != ODS_DD_OK)
        return 20;
    if (ods_daydream_write(&adapter, "Welcome to ODS!\r\n") != ODS_DD_OK)
        return 20;
    return ods_daydream_exit(&adapter, 0) == ODS_DD_OK ? 0 : 20;
}
