/*******************************************************************************
  System Initialization File

  File Name:
    initialization.c

  Summary:
    This file initializes all system components.

  Description:
    This file contains the "SYS_Initialize" function.
*******************************************************************************/

#include "definitions.h"

void SYS_Initialize(void *data)
{
    /* Initialize all enabled peripherals */

    CLK_Initialize();
    GPIO_Initialize();
    TMR1_Initialize();
    UART3_Initialize();

    /* Enable global interrupts */
    __builtin_enable_interrupts();
}
