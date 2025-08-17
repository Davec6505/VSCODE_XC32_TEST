/*******************************************************************************
  System Interrupts File

  File Name:
    interrupts.c

  Summary:
    Interrupt handlers for all system interrupts.

  Description:
    This file contains interrupt handlers for all enabled peripherals.
*******************************************************************************/

#include "definitions.h"

/* Timer1 interrupt handler */
void __ISR(_TIMER_1_VECTOR, ipl4SRS) TIMER_1_Handler(void)
{
    // Clear interrupt flag handled in TMR1_InterruptHandler
    TMR1_InterruptHandler();
}

/* Add other interrupt handlers as needed */
