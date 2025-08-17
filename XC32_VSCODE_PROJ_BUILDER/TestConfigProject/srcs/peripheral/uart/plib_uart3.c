/*******************************************************************************
  UART3 Peripheral Library Source File

  Company:
    Microchip Technology Inc.

  File Name:
    plib_uart3.c

  Summary:
    UART3 peripheral library implementation.

  Description:
    This file contains the source code for UART3 peripheral library.
    
  Configuration:
    Baud Rate: 230400 (9-bit data, no parity)
    BRG Value: 20
*******************************************************************************/

#include "peripheral/uart/plib_uart3.h"
#include "interrupts.h"

// UART3 object
static UART_OBJECT uart3Obj;

void UART3_Initialize(void)
{
    /* Setup UART3 */
    U3MODE = 0x8000 | 0x0008; // Enable UART with configuration
    U3STA = 0x1400;  // Enable TX and RX
    U3BRG = 20;     // 230400 baud @ 80MHz

    uart3Obj.rxBusyStatus = false;
    uart3Obj.txBusyStatus = false;
    
    /* Configure interrupts */
    IFS0bits.U3RXIF = 0;  // Clear RX interrupt flag
    IEC0bits.U3RXIE = 1;  // Enable RX interrupt
    IFS0bits.U3EIF = 0;   // Clear error interrupt flag
    IEC0bits.U3EIE = 1;   // Enable error interrupt
}

bool UART3_SerialSetup(UART_SERIAL_SETUP *setup, uint32_t srcClkFreq)
{
    if (setup == NULL) return false;

    uint32_t brgValue = ((srcClkFreq / setup->baudRate) / 16) - 1;
    U3BRG = brgValue;

    return true;
}

size_t UART3_Read(uint8_t* buffer, const size_t size)
{
    size_t nBytesRead = 0;

    while (nBytesRead < size && U3STAbits.URXDA)
    {
        buffer[nBytesRead++] = U3RXREG;
    }

    return nBytesRead;
}

size_t UART3_Write(uint8_t* buffer, const size_t size)
{
    size_t nBytesWritten = 0;

    while (nBytesWritten < size)
    {
        while (U3STAbits.UTXBF); // Wait for TX buffer space
        U3TXREG = buffer[nBytesWritten++];
    }

    return nBytesWritten;
}

bool UART3_WriteCallbackRegister(UART_CALLBACK callback, uintptr_t context)
{
    uart3Obj.txCallback = callback;
    uart3Obj.txContext = context;
    return true;
}

bool UART3_ReadCallbackRegister(UART_CALLBACK callback, uintptr_t context)
{
    uart3Obj.rxCallback = callback;
    uart3Obj.rxContext = context;
    return true;
}

bool UART3_TransmitComplete(void)
{
    return U3STAbits.TRMT;
}

bool UART3_ReceiverIsReady(void)
{
    return U3STAbits.URXDA;
}

bool UART3_TransmitBufferIsFull(void)
{
    return U3STAbits.UTXBF;
}

uint32_t UART3_ErrorGet(void)
{
    return (U3STA & (_U3STA_OERR_MASK | _U3STA_FERR_MASK | _U3STA_PERR_MASK));
}
