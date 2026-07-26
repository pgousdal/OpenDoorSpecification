#include "ods_daydream.h"

#include <string.h>

static ods_dd_result require_adapter(const ods_daydream *adapter) {
    return adapter == NULL ? ODS_DD_INVALID_ARGUMENT : ODS_DD_OK;
}

static ods_dd_result check_carrier(ods_daydream *adapter) {
    int connected;

    if (require_adapter(adapter) != ODS_DD_OK) {
        return ODS_DD_INVALID_ARGUMENT;
    }
    if (adapter->disconnected) {
        return ODS_DD_DISCONNECTED;
    }
    if (adapter->bindings.carrier == NULL) {
        return ODS_DD_BACKEND_ERROR;
    }

    connected = adapter->bindings.carrier(adapter->bindings.context);
    if (connected <= 0) {
        adapter->disconnected = 1;
        return ODS_DD_DISCONNECTED;
    }
    return ODS_DD_OK;
}

ods_dd_result ods_daydream_init(
    ods_daydream *adapter,
    const ods_dd_bindings *bindings,
    long node
) {
    if (adapter == NULL || bindings == NULL || node < 0) {
        return ODS_DD_INVALID_ARGUMENT;
    }
    memset(adapter, 0, sizeof(*adapter));
    adapter->bindings = *bindings;
    adapter->node = node;
    return ODS_DD_OK;
}

ods_dd_result ods_daydream_write(ods_daydream *adapter, const char *text) {
    ods_dd_result result;
    if (text == NULL) return ODS_DD_INVALID_ARGUMENT;
    result = check_carrier(adapter);
    if (result != ODS_DD_OK) return result;
    if (adapter->bindings.put_str == NULL) return ODS_DD_BACKEND_ERROR;
    return adapter->bindings.put_str(adapter->bindings.context, text) == 0
        ? ODS_DD_OK : ODS_DD_BACKEND_ERROR;
}

ods_dd_result ods_daydream_read_key(ods_daydream *adapter, int *key_out) {
    ods_dd_result result;
    if (key_out == NULL) return ODS_DD_INVALID_ARGUMENT;
    result = check_carrier(adapter);
    if (result != ODS_DD_OK) return result;
    if (adapter->bindings.get_key == NULL) return ODS_DD_BACKEND_ERROR;
    return adapter->bindings.get_key(adapter->bindings.context, key_out) == 0
        ? ODS_DD_OK : ODS_DD_BACKEND_ERROR;
}

ods_dd_result ods_daydream_read_line(
    ods_daydream *adapter,
    char *buffer,
    size_t capacity
) {
    ods_dd_result result;
    if (buffer == NULL || capacity == 0) return ODS_DD_INVALID_ARGUMENT;
    result = check_carrier(adapter);
    if (result != ODS_DD_OK) return result;
    if (adapter->bindings.prompt == NULL) return ODS_DD_BACKEND_ERROR;
    buffer[0] = '\0';
    if (adapter->bindings.prompt(adapter->bindings.context, buffer, capacity) != 0)
        return ODS_DD_BACKEND_ERROR;
    buffer[capacity - 1] = '\0';
    return ODS_DD_OK;
}

ods_dd_result ods_daydream_identity(
    ods_daydream *adapter,
    ods_dd_identity *identity_out
) {
    if (adapter == NULL || identity_out == NULL)
        return ODS_DD_INVALID_ARGUMENT;
    if (adapter->bindings.get_account == NULL) return ODS_DD_BACKEND_ERROR;
    return adapter->bindings.get_account(adapter->bindings.context, identity_out) == 0
        ? ODS_DD_OK : ODS_DD_BACKEND_ERROR;
}

ods_dd_result ods_daydream_node(const ods_daydream *adapter, long *node_out) {
    if (adapter == NULL || node_out == NULL) return ODS_DD_INVALID_ARGUMENT;
    *node_out = adapter->node;
    return ODS_DD_OK;
}

ods_dd_result ods_daydream_time_left(ods_daydream *adapter, long *seconds_out) {
    if (adapter == NULL || seconds_out == NULL)
        return ODS_DD_INVALID_ARGUMENT;
    if (adapter->bindings.time_left == NULL) return ODS_DD_BACKEND_ERROR;
    return adapter->bindings.time_left(adapter->bindings.context, seconds_out) == 0
        ? ODS_DD_OK : ODS_DD_BACKEND_ERROR;
}

ods_dd_result ods_daydream_connection_state(
    ods_daydream *adapter,
    int *connected_out
) {
    int connected;
    if (adapter == NULL || connected_out == NULL)
        return ODS_DD_INVALID_ARGUMENT;
    if (adapter->disconnected) {
        *connected_out = 0;
        return ODS_DD_OK;
    }
    if (adapter->bindings.carrier == NULL) return ODS_DD_BACKEND_ERROR;
    connected = adapter->bindings.carrier(adapter->bindings.context);
    *connected_out = connected > 0;
    if (!*connected_out) adapter->disconnected = 1;
    return ODS_DD_OK;
}

ods_dd_result ods_daydream_set_status(ods_daydream *adapter, const char *text) {
    if (adapter == NULL || text == NULL) return ODS_DD_INVALID_ARGUMENT;
    if (adapter->bindings.change_activity == NULL) return ODS_DD_BACKEND_ERROR;
    return adapter->bindings.change_activity(adapter->bindings.context, text) == 0
        ? ODS_DD_OK : ODS_DD_BACKEND_ERROR;
}

ods_dd_result ods_daydream_command(ods_daydream *adapter, const char *command) {
    ods_dd_result result;
    if (command == NULL) return ODS_DD_INVALID_ARGUMENT;
    result = check_carrier(adapter);
    if (result != ODS_DD_OK) return result;
    if (adapter->bindings.internal_command == NULL) return ODS_DD_BACKEND_ERROR;
    return adapter->bindings.internal_command(adapter->bindings.context, command) == 0
        ? ODS_DD_OK : ODS_DD_BACKEND_ERROR;
}

ods_dd_result ods_daydream_exit(ods_daydream *adapter, int status) {
    if (adapter == NULL) return ODS_DD_INVALID_ARGUMENT;
    adapter->disconnected = 1;
    if (adapter->bindings.close_door == NULL) return ODS_DD_BACKEND_ERROR;
    return adapter->bindings.close_door(adapter->bindings.context, status) == 0
        ? ODS_DD_OK : ODS_DD_BACKEND_ERROR;
}

ods_dd_result ods_daydream_disconnect(ods_daydream *adapter) {
    if (adapter == NULL) return ODS_DD_INVALID_ARGUMENT;
    adapter->disconnected = 1;
    return ODS_DD_OK;
}

const char *ods_daydream_result_string(ods_dd_result result) {
    switch (result) {
        case ODS_DD_OK: return "ok";
        case ODS_DD_DISCONNECTED: return "disconnected";
        case ODS_DD_INVALID_ARGUMENT: return "invalid argument";
        case ODS_DD_BACKEND_ERROR: return "backend error";
        case ODS_DD_BUFFER_TOO_SMALL: return "buffer too small";
        default: return "unknown result";
    }
}
