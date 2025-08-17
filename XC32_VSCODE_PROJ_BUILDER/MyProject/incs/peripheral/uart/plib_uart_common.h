/*******************************************************************************
  UART Peripheral Library Common Interface Header File

  Company:
    Microchip Technology Inc.

  File Name:
    plib_uart_common.h

  Summary:
    UART peripheral library common interface.

  Description:
    This file defines the common interface to the UART peripheral library.
*******************************************************************************/

#ifndef PLIB_UART_COMMON_H
#define PLIB_UART_COMMON_H

#include <stddef.h>
#include <stdbool.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

// UART callback function pointer
typedef void (*UART_CALLBACK)(uintptr_t context);

// UART serial setup structure
typedef struct
{
    uint32_t baudRate;
    uint8_t dataWidth;
    uint8_t parity;
    uint8_t stopBits;
} UART_SERIAL_SETUP;

// UART object structure
typedef struct
{
    UART_CALLBACK txCallback;
    uintptr_t txContext;
    UART_CALLBACK rxCallback;
    uintptr_t rxContext;
    bool txBusyStatus;
    bool rxBusyStatus;
} UART_OBJECT;

#ifdef __cplusplus
}
#endif

#endif /* PLIB_UART_COMMON_H */
