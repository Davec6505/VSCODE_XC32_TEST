/*******************************************************************************
  System Definitions

  File Name:
    definitions.h

  Summary:
    Project system definitions.

  Description:
    This file contains the system-wide inclusions and definitions for TestConfigProject.
*******************************************************************************/

#ifndef DEFINITIONS_H
#define DEFINITIONS_H

#include <stddef.h>
#include <stdbool.h>
#include <stdint.h>
#include "device.h"

// System initialization
void SYS_Initialize(void *data);

// Peripheral includes
#include "peripheral/uart/plib_uart3.h"
#include "peripheral/tmr1/plib_tmr1.h"
#include "peripheral/gpio/plib_gpio.h"
#include "peripheral/clk/plib_clk.h"

#ifdef __cplusplus
extern "C" {
#endif

// System APIs would go here

#ifdef __cplusplus
}
#endif

#endif /* DEFINITIONS_H */
