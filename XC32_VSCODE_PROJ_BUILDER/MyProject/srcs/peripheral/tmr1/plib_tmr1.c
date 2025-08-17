/*******************************************************************************
  TMR1 Peripheral Library Source File

  Company:
    Microchip Technology Inc.

  File Name:
    plib_tmr1.c

  Summary:
    TMR1 peripheral library implementation.

  Description:
    This file contains the source code for TMR1 peripheral library.
    
  Configuration:
    Timer: TMR1 (16-bit)
    Clock Source: PBCLK3
    Prescaler: 1:8 (÷8)
    Period Value: 9999
    Frequency: 1.0 kHz
    Interrupt Priority: 4
*******************************************************************************/

#include "peripheral/tmr1/plib_tmr1.h"
#include "interrupts.h"

// TMR1 object
static TMR1_OBJECT tmr1Obj;

void TMR1_Initialize(void)
{
    /* Setup TMR1 */
    T1CON = 0x0000;  // Stop and reset timer
    TMR1 = 0x0000;   // Clear counter
    PR1 = 9999;     // Period value for 1.0 kHz

    /* Configure Timer Control Register */
    /* 16-bit mode */
    /* Prescaler 1:8 (÷8) */
    /* Internal clock (PBCLK3) */
    T1CON = (1 << _T1CON_TCKPS_POSITION);  // Configure timer

    /* Configure Timer Interrupt */
    IPC1bits.T1IP = 4;  // Priority 4
    IFS0bits.T1IF = 0;  // Clear interrupt flag
    IEC0bits.T1IE = 1;  // Enable interrupt
    
    /* Auto-start timer */
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

void TMR1_CounterSet(uint16_t count)
{
    TMR1 = count;
}

uint32_t TMR1_FrequencyGet(void)
{
    /* Calculate frequency: Input_Clock / (Prescaler * (PR + 1)) */
    uint32_t prescaler_div = 8;
    uint32_t period = PR1 + 1;
    uint32_t input_clock = 80000000;  // Assume 80MHz PBCLK3
    
    return input_clock / (prescaler_div * period);
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
