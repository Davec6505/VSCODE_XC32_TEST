/*******************************************************************************
  TMR1 Peripheral Library Interface Header File

  Company:
    Microchip Technology Inc.

  File Name:
    plib_tmr1.h

  Summary:
    TMR1 peripheral library interface.

  Description:
    This file defines the interface to the TMR1 peripheral library.
    
  Configuration:
    Timer Mode: 16-bit
    Prescaler: 1:8
    Period Mode: Period (ms)
    Frequency: 1.0 kHz
    Interrupt: Enabled
    Priority: 4
*******************************************************************************/

#ifndef PLIB_TMR1_H
#define PLIB_TMR1_H

#include <stddef.h>
#include <stdbool.h>
#include <stdint.h>
#include "device.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef void (*TMR1_CALLBACK)(uint32_t status, uintptr_t context);

typedef struct
{
    TMR1_CALLBACK callback;
    uintptr_t context;
} TMR1_OBJECT;

// TMR1 API
void TMR1_Initialize(void);
void TMR1_Start(void);
void TMR1_Stop(void);
void TMR1_PeriodSet(uint16_t period);
uint16_t TMR1_PeriodGet(void);
uint16_t TMR1_CounterGet(void);
void TMR1_CounterSet(uint16_t count);
uint32_t TMR1_FrequencyGet(void);
bool TMR1_CallbackRegister(TMR1_CALLBACK callback, uintptr_t context);

#ifdef __cplusplus
}
#endif

#endif /* PLIB_TMR1_H */
