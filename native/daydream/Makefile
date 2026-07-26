CC ?= cc
AR ?= ar
CFLAGS ?= -std=c90 -pedantic -Wall -Wextra -Werror -O2
CPPFLAGS ?= -Iinclude
BUILD_DIR ?= build

LIB = $(BUILD_DIR)/libods_daydream.a
OBJ = $(BUILD_DIR)/ods_daydream.o
TEST = $(BUILD_DIR)/test_ods_daydream

.PHONY: all test clean
all: $(LIB)

$(BUILD_DIR):
	mkdir -p $(BUILD_DIR)

$(OBJ): src/ods_daydream.c include/ods_daydream.h | $(BUILD_DIR)
	$(CC) $(CPPFLAGS) $(CFLAGS) -c $< -o $@

$(LIB): $(OBJ)
	$(AR) rcs $@ $^

$(TEST): tests/test_ods_daydream.c $(LIB)
	$(CC) $(CPPFLAGS) $(CFLAGS) $< $(LIB) -o $@

test: $(TEST)
	./$(TEST)

clean:
	rm -rf $(BUILD_DIR)
