#ifndef ODS_DAYDREAM_H
#define ODS_DAYDREAM_H

#include <stddef.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef enum ods_dd_result {
    ODS_DD_OK = 0,
    ODS_DD_DISCONNECTED = 1,
    ODS_DD_INVALID_ARGUMENT = 2,
    ODS_DD_BACKEND_ERROR = 3,
    ODS_DD_BUFFER_TOO_SMALL = 4
} ods_dd_result;

typedef struct ods_dd_identity {
    long user_id;
    const char *display_name;
} ods_dd_identity;

/*
 * The binding table is the only ABI-specific boundary. A small translation
 * unit compiled against the historical DreamDoor SDK supplies these callbacks.
 */
typedef struct ods_dd_bindings {
    void *context;
    int (*carrier)(void *context);
    int (*put_str)(void *context, const char *text);
    int (*get_key)(void *context, int *key_out);
    int (*prompt)(void *context, char *buffer, size_t capacity);
    int (*get_account)(void *context, ods_dd_identity *identity_out);
    int (*time_left)(void *context, long *seconds_out);
    int (*change_activity)(void *context, const char *text);
    int (*internal_command)(void *context, const char *command);
    int (*close_door)(void *context, int status);
} ods_dd_bindings;

typedef struct ods_daydream {
    ods_dd_bindings bindings;
    long node;
    int disconnected;
} ods_daydream;

ods_dd_result ods_daydream_init(
    ods_daydream *adapter,
    const ods_dd_bindings *bindings,
    long node
);

ods_dd_result ods_daydream_write(ods_daydream *adapter, const char *text);
ods_dd_result ods_daydream_read_key(ods_daydream *adapter, int *key_out);
ods_dd_result ods_daydream_read_line(
    ods_daydream *adapter,
    char *buffer,
    size_t capacity
);
ods_dd_result ods_daydream_identity(
    ods_daydream *adapter,
    ods_dd_identity *identity_out
);
ods_dd_result ods_daydream_node(const ods_daydream *adapter, long *node_out);
ods_dd_result ods_daydream_time_left(ods_daydream *adapter, long *seconds_out);
ods_dd_result ods_daydream_connection_state(
    ods_daydream *adapter,
    int *connected_out
);
ods_dd_result ods_daydream_set_status(ods_daydream *adapter, const char *text);
ods_dd_result ods_daydream_command(ods_daydream *adapter, const char *command);
ods_dd_result ods_daydream_exit(ods_daydream *adapter, int status);
ods_dd_result ods_daydream_disconnect(ods_daydream *adapter);

const char *ods_daydream_result_string(ods_dd_result result);

#ifdef __cplusplus
}
#endif

#endif
