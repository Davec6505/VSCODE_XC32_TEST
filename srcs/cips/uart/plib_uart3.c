/*******************************************************************************
  UART3 Peripheral Library Interface Source File

  Company:
    Microchip Technology Inc.

  File Name:
    plib_uart3.c

  Summary:
    UART3 peripheral library source file.

  Description:
    This file implements the interface to the UART3 peripheral library. This
    library provides access to and control of the associated peripheral
    instance.

*******************************************************************************/

// *****************************************************************************
// *****************************************************************************
// Section: Included Files
// *****************************************************************************
// *****************************************************************************

#include <stddef.h>
#include "device.h"
#include "cips/uart/plib_uart3.h"

// *****************************************************************************
// *****************************************************************************
// Section: UART3 Implementation
// *****************************************************************************
// *****************************************************************************

void UART3_Initialize(void)
{
    /* Turn OFF UART3 */
    U3MODE = 0;

    /* Set up UxMODE bits */
    /* STSEL  = 0 (1 stop bit)
     * PDSEL = 00 (8-bit data, no parity)
     * BRGH = 0 (Standard speed mode)
     * RXINV = 0 (IdleState = 1)
     * ABAUD = 0 (Auto-Baud Disabled)
     * LPBACK = 0 (Loop back disabled)
     * WAKE = 0 (Wake up disabled)
     * UEN = 00 (UxTX,UxRX enabled, UxCTS,UxRTS not used)
     * RTSMD = 0 (Simplex mode)
     * IREN = 0 (IrDA encoder and decoder disabled)
     * SIDL = 0 (Halt in Idle mode disabled)
     */
    U3MODE = 0x0;

    /* Enable UART3 Receiver and Transmitter */
    U3STASET = (_U3STA_UTXEN_MASK | _U3STA_URXEN_MASK);

    /* BAUD Rate register Setup */
    /* Baud Rate = 115200 */
    /* Assuming PBCLK2 = 100MHz */
    /* U3BRG = ((100000000 / (16 * 115200)) - 1) = 53.25 ≈ 53 */
    U3BRG = 53;

    /* Turn ON UART3 */
    U3MODESET = _U3MODE_ON_MASK;
}

bool UART3_SerialSetup(UART3_SERIAL_SETUP* setup, uint32_t srcClkFreq)
{
    bool status = false;
    uint32_t baud;
    uint32_t brgValHigh = 0;
    uint32_t brgValLow = 0;

    if (setup != NULL)
    {
        baud = setup->baudRate;

        if (srcClkFreq == 0U)
        {
            srcClkFreq = 100000000UL; /* Default PBCLK2 frequency */
        }

        /* Calculate BRG value */
        brgValLow = ((srcClkFreq / (baud * 16U)) - 1U);
        brgValHigh = ((srcClkFreq / (baud * 4U)) - 1U);

        /* Check if the baud value can be set with low baud settings */
        if ((brgValLow >= 0U) && (brgValLow <= UINT16_MAX))
        {
            /* Turn OFF UART3 */
            U3MODECLR = _U3MODE_ON_MASK;

            if(setup->dataWidth == 9U)
            {
                U3MODESET = _U3MODE_PDSEL0_MASK;
            }
            else
            {
                U3MODECLR = _U3MODE_PDSEL0_MASK;
                U3MODECLR = _U3MODE_PDSEL1_MASK;
            }

            if(setup->parity != 0U)
            {
                U3MODESET = _U3MODE_PDSEL1_MASK;
            }

            if(setup->stopBits == 2U)
            {
                U3MODESET = _U3MODE_STSEL_MASK;
            }
            else
            {
                U3MODECLR = _U3MODE_STSEL_MASK;
            }

            /* BRGH = 0 */
            U3MODECLR = _U3MODE_BRGH_MASK;

            /* Set the BAUD rate */
            U3BRG = brgValLow;

            U3MODESET = _U3MODE_ON_MASK;
            status = true;
        }
        else if ((brgValHigh >= 0U) && (brgValHigh <= UINT16_MAX))
        {
            /* Turn OFF UART3 */
            U3MODECLR = _U3MODE_ON_MASK;

            if(setup->dataWidth == 9U)
            {
                U3MODESET = _U3MODE_PDSEL0_MASK;
            }
            else
            {
                U3MODECLR = _U3MODE_PDSEL0_MASK;
                U3MODECLR = _U3MODE_PDSEL1_MASK;
            }

            if(setup->parity != 0U)
            {
                U3MODESET = _U3MODE_PDSEL1_MASK;
            }

            if(setup->stopBits == 2U)
            {
                U3MODESET = _U3MODE_STSEL_MASK;
            }
            else
            {
                U3MODECLR = _U3MODE_STSEL_MASK;
            }

            /* BRGH = 1 */
            U3MODESET = _U3MODE_BRGH_MASK;

            /* Set the BAUD rate */
            U3BRG = brgValHigh;

            U3MODESET = _U3MODE_ON_MASK;
            status = true;
        }
        else
        {
            /* Do nothing */
        }
    }

    return status;
}

bool UART3_Read(void* buffer, const size_t size)
{
    bool status = false;
    uint8_t* pu8Data = (uint8_t*)buffer;
    size_t processedSize = 0;

    if (pu8Data != NULL)
    {
        /* Clear errors that may have got generated when there was no active read request pending */
        UART3_ErrorGet();

        while (processedSize < size)
        {
            if (UART3_ReceiverIsReady() == true)
            {
                pu8Data[processedSize] = (uint8_t)(U3RXREG);
                processedSize++;
                status = true;
            }
            else
            {
                break;
            }
        }
    }

    return status;
}

bool UART3_Write(void* buffer, const size_t size)
{
    bool status = false;
    uint8_t* pu8Data = (uint8_t*)buffer;
    size_t processedSize = 0;

    if (pu8Data != NULL)
    {
        while (processedSize < size)
        {
            if (UART3_TransmitterIsReady() == true)
            {
                U3TXREG = pu8Data[processedSize];
                processedSize++;
                status = true;
            }
            else
            {
                break;
            }
        }
    }

    return status;
}

int UART3_ReadByte(void)
{
    return (U3RXREG);
}

void UART3_WriteByte(int data)
{
    while ((U3STA & _U3STA_UTXBF_MASK) != 0U)
    {
        /* Do nothing */
    }

    U3TXREG = data;
}

bool UART3_TransmitterIsReady(void)
{
    bool status = false;

    if ((U3STA & _U3STA_UTXBF_MASK) == 0U)
    {
        status = true;
    }

    return status;
}

bool UART3_ReceiverIsReady(void)
{
    bool status = false;

    if ((U3STA & _U3STA_URXDA_MASK) != 0U)
    {
        status = true;
    }

    return status;
}

UART3_ERROR UART3_ErrorGet(void)
{
    UART3_ERROR errors = UART3_ERROR_NONE;
    uint32_t status = U3STA;

    errors = (UART3_ERROR)(status & (_U3STA_OERR_MASK | _U3STA_FERR_MASK | _U3STA_PERR_MASK));

    if (errors != UART3_ERROR_NONE)
    {
        UART3_ErrorClear();
    }

    return errors;
}

void UART3_ErrorClear(void)
{
    /* rxBufferLen = 0; */
    U3STACLR = _U3STA_OERR_MASK;
}

/*******************************************************************************
 End of File
*/
