# Name of the project binary
MODULE := TestConfigProject

# Device configuration
DEVICE := 32MZ1024EFH064

# Cross-platform compiler and DFP paths
ifeq ($(OS),Windows_NT)
    COMPILER_LOCATION := C:/Program Files/Microchip/xc32/v4.60/bin
    DFP_LOCATION := C:/Program Files/Microchip/MPLABX/v6.25/packs
else
    COMPILER_LOCATION := /opt/microchip/xc32/v4.60/bin
    DFP_LOCATION := /opt/microchip/mplabx/v6.25/packs
endif
DFP := $(DFP_LOCATION)/Microchip/PIC32MZ-EF_DFP/1.4.168

# Build system
BUILD=make
CLEAN=make clean
BUILD_DIR=make build_dir

all:
	@echo "######  BUILDING TESTCONFIGPROJECT FOR 32MZ1024EFH064   ########"
	cd srcs && $(BUILD) COMPILER_LOCATION="$(COMPILER_LOCATION)" DFP_LOCATION="$(DFP_LOCATION)" DFP="$(DFP)" DEVICE=$(DEVICE) MODULE=$(MODULE)
	@echo "###### BIN TO HEX ########"
	cd bins && "$(COMPILER_LOCATION)/xc32-bin2hex" $(MODULE)
	@echo "######  BUILD COMPLETE   ########"

build_dir:
	@echo "#######BUILDING DIRECTORIES FOR OUTPUT BINARIES#######"
	cd srcs && $(BUILD_DIR)

clean:
	@echo "####### CLEANING OUTPUTS #######"
	cd srcs && $(CLEAN)

.PHONY: all build_dir clean
