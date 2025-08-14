/*******************************************************************************
  UART3 Peripheral Library Interface Header File

  Company:
    Microchip Technology Inc.

  File Name:
    plib_uart3.h

  Summary:
    UART3 peripheral library interface.

  Description:
    This file defines the interface to the UART3 peripheral library. This
    library provides access to and control of the associated peripheral
    instance.

*******************************************************************************/

#ifndef PLIB_UART3_H    // Guards against multiple inclusion
#define PLIB_UART3_H

// *****************************************************************************
// *****************************************************************************
// Section: Included Files
// *****************************************************************************
// *****************************************************************************

#include <stddef.h>
#include <stdbool.h>
#include <stdint.h>
#include "device.h"

// DOM-IGNORE-BEGIN
#ifdef __cplusplus  // Provide C++ Compatibility

    extern "C" {

#endif
// DOM-IGNORE-END

// *****************************************************************************
// *****************************************************************************
// Section: Data Types
// *****************************************************************************
// *****************************************************************************

// *****************************************************************************
/* UART3 Errors
   Summary:
    Defines the possible errors that can occur during UART operation
*/
typedef enum
{
    UART3_ERROR_NONE = 0,
    UART3_ERROR_OVERRUN = _U3STA_OERR_MASK,
    UART3_ERROR_FRAMING = _U3STA_FERR_MASK,
    UART3_ERROR_PARITY = _U3STA_PERR_MASK

} UART3_ERROR;

// *****************************************************************************
/* UART3 Serial Setup
   Summary:
    Defines the data required to dynamically setup the serial port
*/
typedef struct
{
    uint32_t baudRate;
    uint32_t dataWidth;
    uint32_t parity;
    uint32_t stopBits;

} UART3_SERIAL_SETUP;

// *****************************************************************************
// *****************************************************************************
// Section: UART3 Interface Routines
// *****************************************************************************
// *****************************************************************************

void UART3_Initialize(void);

bool UART3_SerialSetup(UART3_SERIAL_SETUP* setup, uint32_t srcClkFreq);

bool UART3_Read(void* buffer, const size_t size);

bool UART3_Write(void* buffer, const size_t size);

int UART3_ReadByte(void);

void UART3_WriteByte(int data);

bool UART3_TransmitterIsReady(void);

bool UART3_ReceiverIsReady(void);

UART3_ERROR UART3_ErrorGet(void);

void UART3_ErrorClear(void);

// DOM-IGNORE-BEGIN
#ifdef __cplusplus  // Provide C++ Compatibility

    }

#endif
// DOM-IGNORE-END

#endif //PLIB_UART3_H

/*******************************************************************************
 End of File
*/
