/*******************************************************************************
  TMR1 Peripheral Library Source File

  Company:
    Microchip Technology Inc.

  File Name:
    plib_tmr1.c

  Summary:
    TMR1 peripheral library implementation.
*******************************************************************************/

#include "peripheral/tmr1/plib_tmr1.h"

static TMR1_OBJECT tmr1Obj;

void TMR1_Initialize(void)
{
    /* Setup Timer1 */
    T1CON = 0x0000;  // Stop and reset timer
    TMR1 = 0x0000;   // Clear counter
    PR1 = 80000;     // 1ms period @ 80MHz

    // Enable timer interrupt
    IPC1bits.T1IP = 4;  // Priority 4
    IFS0bits.T1IF = 0;  // Clear interrupt flag
    IEC0bits.T1IE = 1;  // Enable interrupt

    T1CONbits.ON = 1;   // Enable timer
}

void TMR1_Start(void)
{
    T1CONbits.ON = 1;
}

void TMR1_Stop(void)
{
    T1CONbits.ON = 0;
}

void TMR1_PeriodSet(uint16_t period)
{
    PR1 = period;
}

uint16_t TMR1_PeriodGet(void)
{
    return PR1;
}

uint16_t TMR1_CounterGet(void)
{
    return TMR1;
}

bool TMR1_CallbackRegister(TMR1_CALLBACK callback, uintptr_t context)
{
    tmr1Obj.callback = callback;
    tmr1Obj.context = context;
    return true;
}

// Interrupt handler (called from interrupts.c)
void TMR1_InterruptHandler(void)
{
    IFS0bits.T1IF = 0;  // Clear interrupt flag

    if (tmr1Obj.callback != NULL)
    {
        tmr1Obj.callback(0, tmr1Obj.context);
    }
}
