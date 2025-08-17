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

#include <stddef.h>                     // Defines NULL
#include <stdbool.h>                    // Defines true
#include <stdlib.h>                     // Defines EXIT_FAILURE
#include <stdint.h>                     // Defines uint32_t, uintptr_t
#include "definitions.h"                // SYS function prototypes
#include "peripheral/tmr1/plib_tmr1.h"
#include "peripheral/uart/plib_uart2.h"
#include "peripheral/gpio/plib_gpio.h"


// *****************************************************************************
// *****************************************************************************
// Variables 
// *****************************************************************************
// *****************************************************************************
static volatile uint32_t millis;
static volatile uint32_t last_millis;

char t;
// *****************************************************************************
// *****************************************************************************
// Callback functions 
// *****************************************************************************
// *****************************************************************************
void T1(uint32_t status, uintptr_t context){
    millis++;
}


void U2( uintptr_t context ){
    
    UART2_Read(&t,1);
    if( t == '0' ){
        LED2_Clear();
    }
    else if( t== '1'){
        LED2_Set();
    }
    UART2_Write(&t,1);
    UART2_Write("\r\n",2);

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
    TMR1_CallbackRegister((TMR1_CALLBACK)T1,0);
    TMR1_Start();
    
    UART2_WriteCallbackRegister( (UART_CALLBACK) U2, 0 );
    UART2_Write("Hello!\r\n",8);
    while ( true )
    {
        /* Maintain state machines of all polled MPLAB Harmony modules. */
        //SYS_Tasks ( );
        if((millis - last_millis) >= 100){
            LED1_Toggle();
            last_millis = millis;
        }
    }

    /* Execution should not come here during normal operation */

    return ( EXIT_FAILURE );
}


/*******************************************************************************
 End of File
*/

