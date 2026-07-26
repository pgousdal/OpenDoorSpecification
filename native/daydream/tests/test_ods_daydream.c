#include "ods_daydream.h"

#include <assert.h>
#include <stdio.h>
#include <string.h>

typedef struct fake_backend {
    int connected;
    int close_status;
    char output[128];
    char activity[64];
} fake_backend;

static int carrier(void *opaque) { return ((fake_backend *)opaque)->connected; }
static int put_str(void *opaque, const char *text) {
    fake_backend *fake = opaque;
    strncat(fake->output, text, sizeof(fake->output) - strlen(fake->output) - 1);
    return 0;
}
static int get_key(void *opaque, int *out) { (void)opaque; *out = 'Y'; return 0; }
static int prompt(void *opaque, char *buffer, size_t capacity) {
    (void)opaque;
    if (capacity > 0) {
        strncpy(buffer, "Open Door", capacity - 1);
        buffer[capacity - 1] = '\0';
    }
    return 0;
}
static int get_account(void *opaque, ods_dd_identity *out) {
    (void)opaque; out->user_id = 42; out->display_name = "Sysop"; return 0;
}
static int time_left(void *opaque, long *out) { (void)opaque; *out = 900; return 0; }
static int change_activity(void *opaque, const char *text) {
    fake_backend *fake = opaque;
    strncpy(fake->activity, text, sizeof(fake->activity) - 1);
    fake->activity[sizeof(fake->activity) - 1] = '\0';
    return 0;
}
static int internal_command(void *opaque, const char *command) {
    (void)opaque; return strcmp(command, "WHO");
}
static int close_door(void *opaque, int status) {
    ((fake_backend *)opaque)->close_status = status; return 0;
}

int main(void) {
    fake_backend fake = {1, -1, "", ""};
    ods_dd_bindings bindings;
    ods_daydream adapter;
    ods_dd_identity identity;
    char line[5];
    int key = 0;
    int connected = 0;
    long value = 0;

    memset(&bindings, 0, sizeof(bindings));
    bindings.context = &fake;
    bindings.carrier = carrier;
    bindings.put_str = put_str;
    bindings.get_key = get_key;
    bindings.prompt = prompt;
    bindings.get_account = get_account;
    bindings.time_left = time_left;
    bindings.change_activity = change_activity;
    bindings.internal_command = internal_command;
    bindings.close_door = close_door;

    assert(ods_daydream_init(&adapter, &bindings, 2) == ODS_DD_OK);
    assert(ods_daydream_write(&adapter, "Hello") == ODS_DD_OK);
    assert(strcmp(fake.output, "Hello") == 0);
    assert(ods_daydream_read_key(&adapter, &key) == ODS_DD_OK && key == 'Y');
    assert(ods_daydream_read_line(&adapter, line, sizeof(line)) == ODS_DD_OK);
    assert(strcmp(line, "Open") == 0);
    assert(ods_daydream_identity(&adapter, &identity) == ODS_DD_OK);
    assert(identity.user_id == 42 && strcmp(identity.display_name, "Sysop") == 0);
    assert(ods_daydream_node(&adapter, &value) == ODS_DD_OK && value == 2);
    assert(ods_daydream_time_left(&adapter, &value) == ODS_DD_OK && value == 900);
    assert(ods_daydream_connection_state(&adapter, &connected) == ODS_DD_OK && connected);
    assert(ods_daydream_set_status(&adapter, "Playing") == ODS_DD_OK);
    assert(strcmp(fake.activity, "Playing") == 0);
    assert(ods_daydream_command(&adapter, "WHO") == ODS_DD_OK);

    fake.connected = 0;
    assert(ods_daydream_write(&adapter, "Never") == ODS_DD_DISCONNECTED);
    assert(strcmp(fake.output, "Hello") == 0);

    adapter.disconnected = 0;
    fake.connected = 1;
    assert(ods_daydream_exit(&adapter, 7) == ODS_DD_OK);
    assert(fake.close_status == 7);

    puts("native DayDream adapter tests passed");
    return 0;
}
