/*******************************************************************************
  UART2 Peripheral Library Interface Header File

  Company:
    Microchip Technology Inc.

  File Name:
    plib_uart2.h

  Summary:
    UART2 peripheral library interface.

  Description:
    This file defines the interface to the UART2 peripheral library.
    
  Configuration:
    Baud Rate: 115200
    Data Bits: 8
    Parity: None
    Stop Bits: 1
*******************************************************************************/

#ifndef PLIB_UART2_H
#define PLIB_UART2_H

#include <stddef.h>
#include <stdbool.h>
#include <stdint.h>
#include "device.h"
#include "plib_uart_common.h"

#ifdef __cplusplus
extern "C" {
#endif

// UART2 API
void UART2_Initialize(void);
bool UART2_SerialSetup(UART_SERIAL_SETUP *setup, uint32_t srcClkFreq);
size_t UART2_Read(uint8_t* buffer, const size_t size);
size_t UART2_Write(uint8_t* buffer, const size_t size);
bool UART2_WriteCallbackRegister(UART_CALLBACK callback, uintptr_t context);
bool UART2_ReadCallbackRegister(UART_CALLBACK callback, uintptr_t context);
bool UART2_TransmitComplete(void);
bool UART2_ReceiverIsReady(void);
bool UART2_TransmitBufferIsFull(void);
uint32_t UART2_ErrorGet(void);

#ifdef __cplusplus
}
#endif

#endif /* PLIB_UART2_H */
