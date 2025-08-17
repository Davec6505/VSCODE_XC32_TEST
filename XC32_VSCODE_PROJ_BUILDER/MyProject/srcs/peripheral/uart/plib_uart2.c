/*******************************************************************************
  UART2 Peripheral Library Source File

  Company:
    Microchip Technology Inc.

  File Name:
    plib_uart2.c

  Summary:
    UART2 peripheral library implementation.

  Description:
    This file contains the source code for UART2 peripheral library.
    
  Configuration:
    Baud Rate: 115200 (8-bit data, no parity)
    BRG Value: 42
*******************************************************************************/

#include "peripheral/uart/plib_uart2.h"
#include "interrupts.h"

// UART2 object
static UART_OBJECT uart2Obj;

void UART2_Initialize(void)
{
    /* Setup UART2 */
    U2MODE = 0x8000 | 0x0000; // Enable UART with configuration
    U2STA = 0x1400;  // Enable TX and RX
    U2BRG = 42;     // 115200 baud @ 80MHz

    uart2Obj.rxBusyStatus = false;
    uart2Obj.txBusyStatus = false;
    
    /* Configure interrupts */
    IFS0bits.U2RXIF = 0;  // Clear RX interrupt flag
    IEC0bits.U2RXIE = 1;  // Enable RX interrupt
    IFS0bits.U2EIF = 0;   // Clear error interrupt flag
    IEC0bits.U2EIE = 1;   // Enable error interrupt
}

bool UART2_SerialSetup(UART_SERIAL_SETUP *setup, uint32_t srcClkFreq)
{
    if (setup == NULL) return false;

    uint32_t brgValue = ((srcClkFreq / setup->baudRate) / 16) - 1;
    U2BRG = brgValue;

    return true;
}

size_t UART2_Read(uint8_t* buffer, const size_t size)
{
    size_t nBytesRead = 0;

    while (nBytesRead < size && U2STAbits.URXDA)
    {
        buffer[nBytesRead++] = U2RXREG;
    }

    return nBytesRead;
}

size_t UART2_Write(uint8_t* buffer, const size_t size)
{
    size_t nBytesWritten = 0;

    while (nBytesWritten < size)
    {
        while (U2STAbits.UTXBF); // Wait for TX buffer space
        U2TXREG = buffer[nBytesWritten++];
    }

    return nBytesWritten;
}

bool UART2_WriteCallbackRegister(UART_CALLBACK callback, uintptr_t context)
{
    uart2Obj.txCallback = callback;
    uart2Obj.txContext = context;
    return true;
}

bool UART2_ReadCallbackRegister(UART_CALLBACK callback, uintptr_t context)
{
    uart2Obj.rxCallback = callback;
    uart2Obj.rxContext = context;
    return true;
}

bool UART2_TransmitComplete(void)
{
    return U2STAbits.TRMT;
}

bool UART2_ReceiverIsReady(void)
{
    return U2STAbits.URXDA;
}

bool UART2_TransmitBufferIsFull(void)
{
    return U2STAbits.UTXBF;
}

uint32_t UART2_ErrorGet(void)
{
    return (U2STA & (_U2STA_OERR_MASK | _U2STA_FERR_MASK | _U2STA_PERR_MASK));
}
