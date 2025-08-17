/*******************************************************************************
  GPIO Peripheral Library Source File

  Company:
    Microchip Technology Inc.

  File Name:
    plib_gpio.c

  Summary:
    GPIO peripheral library implementation.
*******************************************************************************/

#include "peripheral/gpio/plib_gpio.h"

void GPIO_Initialize(void)
{
    /* Configure LED pins as outputs */
    TRISBCLR = (1<<8) | (1<<9); // RB8, RB9 as outputs (LED1, LED2)
    LATBCLR = (1<<8) | (1<<9);  // Clear LEDs initially

    /* Configure button pins as inputs */
    TRISASET = (1<<6) | (1<<7); // RA6, RA7 as inputs (BTN1, BTN2)

    /* Configure other pins as needed */
    // Add additional GPIO configuration here
}
