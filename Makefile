# Name of the project binary
MODULE    	:= VS_XC32_CNC

# Device configuration
# The device is expected to be a PIC32MZ family device.
DEVICE 		:= 32MZ1024EFH064

# Compiler location and DFP (Device Family Pack) location
# The compiler location is expected to be the path to the xc32-gcc compiler.
# The DFP location is expected to be the path to the Microchip Device Family Pack.
# The DFP is used to provide the necessary header files and libraries for the specific device.
# The DFP is expected to be installed in the MPLAB X IDE installation directory.
# The DFP is expected to be in the packs directory of the MPLAB X IDE installation directory.
# The DFP is expected to be in the format of Microchip/PIC32MZ-EF_DFP/1.4.168.
# Cross-platform compiler and DFP paths
ifeq ($(OS),Windows_NT)
    COMPILER_LOCATION := C:/Program Files/Microchip/xc32/v4.60/bin
    DFP_LOCATION := C:/Program Files/Microchip/MPLABX/v6.25/packs
else
    COMPILER_LOCATION := /opt/microchip/xc32/v4.60/bin
    DFP_LOCATION := /opt/microchip/mplabx/v6.25/packs
endif
DFP := $(DFP_LOCATION)/Microchip/PIC32MZ-EF_DFP/1.4.168
#\Microchip\PIC32MZ-EF_DFP\1.4.168\xc32\32MZ1024EFH064

# Simple Unix-style build system
BUILD=make
CLEAN=make clean
BUILD_DIR=make build_dir
#THIRDP_LIB_PATH=/usr/local/mylibs/

all:
	@echo "######  BUILDING   ########"
	cd srcs && $(BUILD) COMPILER_LOCATION="$(COMPILER_LOCATION)" DFP_LOCATION="$(DFP_LOCATION)" DFP="$(DFP)" DEVICE=$(DEVICE) MODULE=$(MODULE)
	@echo "###### BIN TO HEX ########"
	cd bins && "$(COMPILER_LOCATION)/xc32-bin2hex" $(MODULE)
	@echo "######  BUILD COMPLETE   ########"

3rd-party-libs:
#	(cd src/3rd_party/libzmq; $(BUILD) install)

build_dir:
	@echo "#######BUILDING DIRECTORIES FOR OUTPUT BINARIES#######"
	cd srcs && $(BUILD_DIR)

debug:
	@echo "#######DEBUGGING OUTPUTS#######"
	cd srcs && $(BUILD) debug COMPILER_LOCATION="$(COMPILER_LOCATION)" DFP_LOCATION="$(DFP_LOCATION)" DFP="$(DFP)" DEVICE=$(DEVICE) MODULE=$(MODULE)

clean:
	@echo "####### CLEANING OUTPUTS #######"
	cd srcs && $(CLEAN)
	@echo "####### REMOVING BUILD ARTIFACTS #######"
ifeq ($(OS),Windows_NT)
	@"C:\Program Files\Git\bin\bash.exe" -c "rm -rf bins/* objs/* other/* 2>/dev/null || true"
else
	@rm -rf bins/* objs/* other/* 2>/dev/null || true
endif

install:
	cd srcs && $(BUILD) install

flash:
	@echo "#######LOADING OUTPUTS#######"
	cd bins && sudo ../../MikroC_bootloader_lnx/bins/mikro_hb $(MODULE).hex
	@echo "#######LOAD COMPLETE#######"


dfp_dir:
	@echo "####### DFP DIRECTORY #######"
	@echo $(DFP)

help:
	@echo "####### HELP #######"
	cd srcs && $(BUILD) help
	@echo "#####################"

# Unix-style utility targets (cross-platform)
find-source:
	@echo "####### FINDING SOURCE FILES #######"
ifeq ($(OS),Windows_NT)
	@"C:\Program Files\Git\bin\bash.exe" -c "find srcs -name '*.c' -o -name '*.h'"
else
	@find srcs -name "*.c" -o -name "*.h"
endif

grep-pattern:
	@echo "####### SEARCHING FOR PATTERN (usage: make grep-pattern PATTERN=your_pattern) #######"
ifeq ($(OS),Windows_NT)
	@"C:\Program Files\Git\bin\bash.exe" -c "grep -r '$(PATTERN)' srcs/ || echo 'No matches found'"
else
	@grep -r "$(PATTERN)" srcs/ || echo "No matches found"
endif

list-files:
	@echo "####### LISTING PROJECT FILES #######"
ifeq ($(OS),Windows_NT)
	@"C:\Program Files\Git\bin\bash.exe" -c "ls -la"
else
	@ls -la
endif

.PHONY: all 3rd-party-libs build_dir clean install find-source grep-pattern list-files