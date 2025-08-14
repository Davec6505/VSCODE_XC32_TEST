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
#include <string.h>                     // Defines strlen
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

    /* Send initial message via UART3 */
    const char* welcome_msg = "UART3 Initialized - PIC32 Running!\r\n";
    UART3_Write((void*)welcome_msg, strlen(welcome_msg));

    uint32_t last_toggle = 0;
    uint32_t last_uart_msg = 0;
    while ( true )
    {
        /* Maintain state machines of all polled MPLAB Harmony modules. */
        if ((millisec - last_toggle) >= 100) {
            LED1_Toggle();
            last_toggle = millisec;
        }
        
        /* Send periodic UART message every 1000ms */
        if ((millisec - last_uart_msg) >= 1000) {
            const char* status_msg = "System running... millisec = ";
            UART3_Write((void*)status_msg, strlen(status_msg));
            
            /* Simple integer to string conversion for millisec */
            char num_str[12];
            uint32_t num = millisec;
            int i = 0;
            if (num == 0) {
                num_str[i++] = '0';
            } else {
                while (num > 0) {
                    num_str[i++] = '0' + (num % 10);
                    num /= 10;
                }
            }
            /* Reverse the string */
            for (int j = 0; j < i/2; j++) {
                char temp = num_str[j];
                num_str[j] = num_str[i-1-j];
                num_str[i-1-j] = temp;
            }
            num_str[i] = '\0';
            
            UART3_Write((void*)num_str, strlen(num_str));
            UART3_Write((void*)"\r\n", 2);
            
            last_uart_msg = millisec;
        }
    }

    /* Execution should not come here during normal operation */

    return ( EXIT_FAILURE );
}


/*******************************************************************************
 End of File
*/

