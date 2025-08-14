# DFP (Device Family Pack) configuration
# These variables should be passed from the root Makefile
DFP_DIR := $(DFP)
DFP_INCLUDE := $(DFP)/include

# Project directories expected in the project.
# These directories are created if they do not exist when "make build_dir" is run.
# The directories are used to store object files, binaries, source files, include files, and other files.
# The directories are created relative to the project root directory.
# The project root directory is expected to be one level above the srcs directory.
# The project root directory is expected to contain the srcs, objs, incs, bins, and other directories.
# The objs directory is used to store object files.
# The incs directory is used to store header files.
# The bins directory is used to store binaries.
# The other directory is used to store other files such as maps and XML files.
ROOT     := ..
OBJ_DIR  := $(ROOT)/objs
INC_DIR  := $(ROOT)/incs
BIN_DIR  := $(ROOT)/bins
SRC_DIR  := $(ROOT)/srcs
OUT_DIR  := $(ROOT)/other


# Source files and object files
# The source files are expected to be in the srcs directory & sub-directories.
# The source files are expected to have the .c extension.
# The object file list is created from the SRCS variable with the .o extension inplaceof the .c extension.
# Dynamically find all .c files using Make functions (up to 4 levels deep)
define get_c_files
$(wildcard $(1)/*.c) $(wildcard $(1)/*/*.c) $(wildcard $(1)/*/*/*.c) $(wildcard $(1)/*/*/*/*.c)
endef
SRCS := $(call get_c_files,$(SRC_DIR))
OBJS := $(SRCS:$(SRC_DIR)/%.c=$(OBJ_DIR)/%.o)


# The assembly files are expected to be in the srcs directory & sub-directories.
# Dynamically find all .S files using Make functions (up to 4 levels deep)
define get_s_files
$(wildcard $(1)/*.S) $(wildcard $(1)/*/*.S) $(wildcard $(1)/*/*/*.S) $(wildcard $(1)/*/*/*/*.S)
endef
ASM := $(call get_s_files,$(SRC_DIR))
ASMS := $(ASM:$(SRC_DIR)/%.S=$(OBJ_DIR)/%.o)

# The assembly object files are created from the ASM variable with the .o extension inplace of the .S extension.
# The assembly object files are added to the OBJS variable.
# This allows the assembly files to be compiled and linked with the C source files.
# The assembly files are expected to be in the srcs directory & sub-directories.
# The assembly files are expected to have the .S extension.
# The assembly files are expected to be compiled with the same compiler as the C source files.
# The assembly files are expected to be compiled with the same flags as the C source files.
OBJS += $(ASMS)

# Compiler and flags
COMPILER  := c99
ifeq ($(COMPILER),c99)
CC := "$(COMPILER_LOCATION)/xc32-gcc"
MCU := -mprocessor=$(DEVICE)
STD := c99
FLAGS := -Werror -Wall -MP -MMD
else
CC := "$(COMPILER_LOCATION)/xc32"
MCU := -mprocessor=$(DEVICE)
STD := c90
endif


# Assign all Include directories dynamically, first run "make build_dir" from terminal.
INCS := -I"$(INC_DIR)" -I"$(DFP_INCLUDE)"
#INCS := $(foreach d,$(shell dir /s /b /ad $(INC_DIR) 2>nul),-I$d) $(foreach d,$(INC_DIR),-I$d)
#INCS := $(foreach d,$(shell find $(INC_DIR) -type d),-I$d)
#INCS +=   -I$(DFP_INCLUDE)


#Direct the compiler outputs for .o files from .c or .cpp code
DIRECT_OBJ := $(CC)    -g -x c -c $(MCU)  -ffunction-sections -fdata-sections -O1 -fno-common \
			$(INCS)  $(FLAGS) -MF $(@:.o=.d) -DXPRJ_default=default -mdfp="$(DFP)"
			

# Direct compiler output for linker 
LINKER_SCRIPT := $(DFP)/xc32/$(DEVICE)/p32MZ1024EFH064.ld
DIRECT_LINK := $(CC)  $(MCU) -nostartfiles -DXPRJ_default=default -mdfp="$(DFP)" 	\
			-Wl,--defsym=__MPLAB_BUILD=1,--script="$(LINKER_SCRIPT)",--defsym=_min_heap_size=512,--gc-sections,--no-code-in-dinit,--no-dinit-in-serial-mem,-Map="$(OUT_DIR)/production.map",--memorysummary,$(OUT_DIR)/memoryfile.xml \




DIRECT_ASM :=   -c  -DXPRJ_default=default    -Wa,--defsym=__MPLAB_BUILD=1,-MD=$(OBJ_DIR)/startup/startup.o.asm.d,--gdwarf-2 -mdfp="$(DFP)" -MMD -MF $(OBJ_DIR)/startup/startup.o.d

# Define the default target (which is built when make is invoked without any arguments)
$(BIN_DIR)/$(MODULE): $(OBJS)
	@echo "Building project for $(DEVICE)"
	@echo "Linking object files to create the final executable"
	$(DIRECT_LINK) -o $@ $^ 
	@echo "Build complete. Output is in $(BIN_DIR)"

# Compile all source files to object files
$(OBJ_DIR)/%.o: $(SRC_DIR)/%.c
	@echo "Compiling $< to $@"
ifeq ($(OS),Windows_NT)
	@if not exist "$(subst /,\,$(dir $@))" mkdir "$(subst /,\,$(dir $@))"
else
	@mkdir -p $(dir $@)
endif
	$(DIRECT_OBJ) $< -o $@
	@echo "Object file created: $@"

$(OBJ_DIR)/%.o: $(SRC_DIR)/%.S
	@echo "Compiling assembly file $< to object file $@"
ifeq ($(OS),Windows_NT)
	@if not exist "$(subst /,\,$(dir $@))" mkdir "$(subst /,\,$(dir $@))"
else
	@mkdir -p $(dir $@)
endif
	$(CC) $(MCU) $(DIRECT_ASM) -o $@ $<
	@echo "Object file created: $@"



.PHONY: clean build_dir debug help

# Create the build directories if they do not exist
# This target is used to create the necessary directories for the build process.
# It creates the OBJ_DIR, BIN_DIR, SRC_DIR, INC_DIR, and OUT_DIR
# It also creates subdirectories in OBJ_DIR and INC_DIR for each subdirectory in SRC_DIR
# This is useful for organizing the build output and include files.
# To run this target, use: make build_dir
# Get all directories under SRC_DIR dynamically (similar to how we get source files)
SRC_DIRS := $(sort $(dir $(wildcard $(SRC_DIR)/*/)) $(dir $(wildcard $(SRC_DIR)/*/*/)) $(dir $(wildcard $(SRC_DIR)/*/*/*/)))
# Filter out startup directory from automatic creation
SRC_SUBDIRS := $(sort $(filter-out startup/,$(SRC_DIRS:$(SRC_DIR)/%=%)))

build_dir: 
	@echo "Creating build base directories if they do not exist"
ifeq ($(OS),Windows_NT)
	@if not exist "$(OBJ_DIR)" mkdir "$(OBJ_DIR)"
	@if not exist "$(BIN_DIR)" mkdir "$(BIN_DIR)"
	@if not exist "$(SRC_DIR)" mkdir "$(SRC_DIR)"
	@if not exist "$(INC_DIR)" mkdir "$(INC_DIR)"
	@if not exist "$(OUT_DIR)" mkdir "$(OUT_DIR)"
	@echo "Creating subdirectories in OBJ_DIR and INC_DIR based on SRC_DIR structure (excluding startup from incs)"
	@if not exist "$(OBJ_DIR)\startup" mkdir "$(OBJ_DIR)\startup"
	@echo "Created: $(OBJ_DIR)/startup (object files only)"
else
	@mkdir -p $(OBJ_DIR) $(BIN_DIR) $(SRC_DIR) $(INC_DIR) $(OUT_DIR)
	@echo "Creating subdirectories in OBJ_DIR and INC_DIR based on SRC_DIR structure (excluding startup from incs)"
	@mkdir -p $(OBJ_DIR)/startup
	@echo "Created: $(OBJ_DIR)/startup (object files only)"
	@$(foreach subdir,$(SRC_SUBDIRS),mkdir -p $(OBJ_DIR)/$(subdir) $(INC_DIR)/$(subdir) && echo "Created: $(OBJ_DIR)/$(subdir) and $(INC_DIR)/$(subdir)" &&) true
	@echo "Moving header files from src subdirectories to corresponding inc subdirectories"
	@$(foreach subdir,$(SRC_SUBDIRS),$(foreach header,$(wildcard $(SRC_DIR)/$(subdir)*.h),mv $(header) $(INC_DIR)/$(subdir) && echo "Moved: $(header) -> $(INC_DIR)/$(subdir)" &&)) true
endif
	@echo "Build directories created successfully"

# Display the source files, object files, and include directories
debug:
	@echo "Source files:"
	@echo $(SRCS)
	@echo "Object files:"
	@echo $(OBJS)
	@echo "Include directories:"
	@echo $(INCS)
	@echo "Linker script:"
	@echo $(LINKER_SCRIPT)


# For xc32 Compiler help with less use: make help less
# For xc32 Compiler help without less use: make help
help:
	@echo "Displaying help information for xc32-gcc"
ifeq ($(filter less,$(MAKECMDGOALS)),less)
	xc32-gcc --help | less
else
	xc32-gcc --help
endif





clean:
	@echo "Cleaning up object files and binaries"
ifeq ($(OS),Windows_NT)
	@if exist "$(BIN_DIR)\*" del /q "$(BIN_DIR)\*" >nul 2>&1
	@if exist "$(OBJ_DIR)\*" rmdir /s /q "$(OBJ_DIR)" >nul 2>&1 && mkdir "$(OBJ_DIR)" >nul 2>&1
	@if exist "$(OUT_DIR)\*" del /q "$(OUT_DIR)\*" >nul 2>&1
else
	@rm -rf $(BIN_DIR)/* $(OBJ_DIR)/* $(OUT_DIR)/* 2>/dev/null || true
endif
	@echo "Clean complete."


define clear_build_dir
	-@rm -rf $(BIN_DIR)/* $(OBJ_DIR)/* $(OUT_DIR)/* 2>/dev/null || true
endef



##################################################################################################
##                       Table 5-6. Kind-of-Output Control Options								##
##################################################################################################
# Option      |  Definition
# -----------------------------------------------------------------------------------------------
# -c          |  Stop compilation before the link step, producing an intermediate file.
# -E          |  Stop compilation after preprocessing, producing a preprocessed file.
# --help      |  Print a description of the command line options.
# -o file     |Place the output in a file with the specified name.
# -S          |  Stop compilation before the assembly step, producing an assembly file output.
# -specs=file |  Overrides the standard specs file.
# -v          |  Print the commands executed during each stage of compilation.
# --version   |  Show version information then quit.
# -x          |  Specify the language of a source file regardless of its file extension.
#################################################################################################