/*******************************************************************************
  GPIO Peripheral Library Interface Header File

  Company:
    Microchip Technology Inc.

  File Name:
    plib_gpio.h

  Summary:
    GPIO peripheral library interface.
*******************************************************************************/

#ifndef PLIB_GPIO_H
#define PLIB_GPIO_H

#include <stdint.h>
#include <stdbool.h>
#include "device.h"

#ifdef __cplusplus
extern "C" {
#endif

// GPIO pin definitions for PIC32MZ Clicker
#define LED1_Set()          (LATBSET = (1<<8))
#define LED1_Clear()        (LATBCLR = (1<<8))
#define LED1_Toggle()       (LATBINV = (1<<8))
#define LED1_Get()          ((PORTB >> 8) & 0x1)
#define LED1_OutputEnable() (TRISBCLR = (1<<8))

#define LED2_Set()          (LATBSET = (1<<9))
#define LED2_Clear()        (LATBCLR = (1<<9))
#define LED2_Toggle()       (LATBINV = (1<<9))
#define LED2_Get()          ((PORTB >> 9) & 0x1)
#define LED2_OutputEnable() (TRISBCLR = (1<<9))

// Button definitions
#define BTN1_Get()          ((PORTA >> 6) & 0x1)
#define BTN1_InputEnable()  (TRISASET = (1<<6))

#define BTN2_Get()          ((PORTA >> 7) & 0x1)
#define BTN2_InputEnable()  (TRISASET = (1<<7))

void GPIO_Initialize(void);

#ifdef __cplusplus
}
#endif

#endif /* PLIB_GPIO_H */
