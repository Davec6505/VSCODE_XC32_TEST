/*******************************************************************************
  CLK Peripheral Library Interface Header File

  Company:
    Microchip Technology Inc.

  File Name:
    plib_clk.h

  Summary:
    CLK peripheral library interface.
    
  Description:
    Generated clock configuration based on user settings:
    - Primary Oscillator: HS (12.0 MHz)
    - PLL: Enabled
    - System Frequency: 80.0 MHz
    - Peripheral Frequency: 80.0 MHz
*******************************************************************************/

#ifndef PLIB_CLK_H
#define PLIB_CLK_H

#include <stdint.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

// Clock configuration constants
#define CLK_SYSTEM_FREQUENCY    80000000UL
#define CLK_PERIPHERAL_FREQUENCY 80000000UL
#define CLK_INPUT_FREQUENCY     12000000UL

// Oscillator configuration
#define CLK_PRIMARY_OSC         "HS"
#define CLK_PLL_ENABLED         1

// PLL Configuration
#define CLK_PLL_INPUT_DIV       2
#define CLK_PLL_MULTIPLIER      15
#define CLK_PLL_OUTPUT_DIV      1

// Peripheral Bus Clock Configuration
// PIC32MZ PBCLK Assignments (based on datasheet):
//   PBCLK1: CPU/System Bus - CPU instructions, system bus
//   PBCLK2: UART/SPI/I2C Peripherals - Serial communication modules  
//   PBCLK3: Timer/PWM/Input Capture/Output Compare - Time-based peripherals
//   PBCLK4: Ports/Change Notification - GPIO and pin change notifications
//   PBCLK5: Flash Controller/Crypto - Flash memory and cryptographic engine
//   PBCLK6: USB/CAN/Ethernet - High-speed communication interfaces
//   PBCLK7: CPU Trace/Debug - Development and debugging features
// Register Values: 1=÷1 (no division), 2=÷2, 3=÷3, etc.
#define CLK_PBCLK1_ENABLED       1
#define CLK_PBCLK1_FREQUENCY     80000000UL
#define CLK_PBCLK1_DIVIDER_REG   0
#define CLK_PBCLK1_DIVIDER_VAL   1
#define CLK_PBCLK2_ENABLED       1
#define CLK_PBCLK2_FREQUENCY     80000000UL
#define CLK_PBCLK2_DIVIDER_REG   0
#define CLK_PBCLK2_DIVIDER_VAL   1
#define CLK_PBCLK3_ENABLED       1
#define CLK_PBCLK3_FREQUENCY     80000000UL
#define CLK_PBCLK3_DIVIDER_REG   0
#define CLK_PBCLK3_DIVIDER_VAL   1
#define CLK_PBCLK4_ENABLED       0
#define CLK_PBCLK4_FREQUENCY     0UL
#define CLK_PBCLK4_DIVIDER_REG   0
#define CLK_PBCLK4_DIVIDER_VAL   1
#define CLK_PBCLK5_ENABLED       0
#define CLK_PBCLK5_FREQUENCY     0UL
#define CLK_PBCLK5_DIVIDER_REG   0
#define CLK_PBCLK5_DIVIDER_VAL   1
#define CLK_PBCLK6_ENABLED       0
#define CLK_PBCLK6_FREQUENCY     0UL
#define CLK_PBCLK6_DIVIDER_REG   0
#define CLK_PBCLK6_DIVIDER_VAL   1
#define CLK_PBCLK7_ENABLED       0
#define CLK_PBCLK7_FREQUENCY     0UL
#define CLK_PBCLK7_DIVIDER_REG   0
#define CLK_PBCLK7_DIVIDER_VAL   1

// Clock API
void CLK_Initialize(void);
uint32_t CLK_SystemFrequencyGet(void);
uint32_t CLK_PeripheralFrequencyGet(void);
uint32_t CLK_InputFrequencyGet(void);
bool CLK_PLLIsEnabled(void);

// PBCLK API
uint32_t CLK_PBCLKFrequencyGet(uint8_t pbclkNum);
bool CLK_PBCLKIsEnabled(uint8_t pbclkNum);

#ifdef __cplusplus
}
#endif

#endif /* PLIB_CLK_H */
