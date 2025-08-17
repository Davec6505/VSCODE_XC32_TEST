/*******************************************************************************
  UART3 Peripheral Library Interface Header File

  Company:
    Microchip Technology Inc.

  File Name:
    plib_uart3.h

  Summary:
    UART3 peripheral library interface.

  Description:
    This file defines the interface to the UART3 peripheral library.
    
  Configuration:
    Baud Rate: 230400
    Data Bits: 9
    Parity: None
    Stop Bits: 1
*******************************************************************************/

#ifndef PLIB_UART3_H
#define PLIB_UART3_H

#include <stddef.h>
#include <stdbool.h>
#include <stdint.h>
#include "device.h"
#include "plib_uart_common.h"

#ifdef __cplusplus
extern "C" {
#endif

// UART3 API
void UART3_Initialize(void);
bool UART3_SerialSetup(UART_SERIAL_SETUP *setup, uint32_t srcClkFreq);
size_t UART3_Read(uint8_t* buffer, const size_t size);
size_t UART3_Write(uint8_t* buffer, const size_t size);
bool UART3_WriteCallbackRegister(UART_CALLBACK callback, uintptr_t context);
bool UART3_ReadCallbackRegister(UART_CALLBACK callback, uintptr_t context);
bool UART3_TransmitComplete(void);
bool UART3_ReceiverIsReady(void);
bool UART3_TransmitBufferIsFull(void);
uint32_t UART3_ErrorGet(void);

#ifdef __cplusplus
}
#endif

#endif /* PLIB_UART3_H */
