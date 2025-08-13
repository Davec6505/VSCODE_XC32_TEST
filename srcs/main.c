/*******************************************************************************
  Main Source File

  Company:
    Microchip Technology Inc.

  File Name:
    main.c

  Summary:
    This file contains the "main" function for a project.

  Description:
    This file contains the "main" function for a project.  The
    "main" function calls the "SYS_Initialize" function to initialize the state
    machines of all modules in the system
 *******************************************************************************/

// *****************************************************************************
// *****************************************************************************
// Section: Included Files
// *****************************************************************************
// *****************************************************************************


#include <xc.h>                          // PIC32 SFR definitions
#include <stddef.h>                     // Defines NULL
#include <stdbool.h>                    // Defines true
#include <stdlib.h>                     // Defines EXIT_FAILURE
#include <stdint.h>                     // Defines uint32_t
#include "../incs/definitions.h"         // SYS function prototypes
#include "../incs/cips/gpio/plib_gpio.h" // LED macros and SFRs






volatile uint32_t millisec = 0;

void T1(uint32_t status, uintptr_t context){
  /* Timer 1 callback function */
  millisec++;

  // Toggle LED2 for debug: should blink fast if timer/interrupts work
  LED2_Toggle();
}


// *****************************************************************************
// *****************************************************************************
// Section: Main Entry Point
// *****************************************************************************
// *****************************************************************************

int main ( void )
{
    /* Initialize all modules */
    SYS_Initialize ( NULL );

  TMR1_CallbackRegister(T1, 0);
  TMR1_Start();

 

  uint32_t last_toggle = 0;
  while ( true )
  {
    /* Maintain state machines of all polled MPLAB Harmony modules. */
    if ((millisec - last_toggle) >= 100) {
      LED1_Toggle();
      last_toggle = millisec;
    }

  }

    /* Execution should not come here during normal operation */

    return ( EXIT_FAILURE );
}


/*******************************************************************************
 End of File
*/

