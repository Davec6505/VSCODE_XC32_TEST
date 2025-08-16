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
#include <stdio.h>                      // Defines sprintf
#include "../incs/definitions.h"         // SYS function prototypes
#include "../incs/cips/gpio/plib_gpio.h" // LED macros and SFRs
#include "../incs/uart2_test.h"          // Simple UART2 test functions






volatile uint32_t millisec = 0;

void T1(uint32_t status, uintptr_t context){
  /* Timer 1 callback function */
  millisec++;
}

void UART2_RxCallback(uintptr_t context)
{
    /* UART2 receive interrupt callback */
    char receivedChar;
    
    /* Read the received character */
    if (UART2_ReceiverIsReady())
    {
        receivedChar = (char)UART2_ReadByte();
        
        /* Handle special commands for Timer control */
        if (receivedChar == '2')
        {
            TMR2_Start();
            const char* msg = "TMR2 STARTED (500ms LED2 ON)\r\n";
            UART2_Write((void*)msg, strlen(msg));
        }
        else if (receivedChar == '3')
        {
            TMR3_Start();
            const char* msg = "TMR3 STARTED (250ms LED2 OFF)\r\n";
            UART2_Write((void*)msg, strlen(msg));
        }
        else if (receivedChar == 'x' || receivedChar == 'X')
        {
            TMR2_Stop();
            TMR3_Stop();
            const char* msg = "TMR2 and TMR3 STOPPED\r\n";
            UART2_Write((void*)msg, strlen(msg));
        }
        else if (receivedChar == 's' || receivedChar == 'S')
        {
            const char* status_msg = "Status: TMR2=LED2_ON(500ms), TMR3=LED2_OFF(250ms)\r\n";
            UART2_Write((void*)status_msg, strlen(status_msg));
        }
        else
        {
            /* Echo the character back */
            UART2_WriteByte(receivedChar);
            
            /* Add line feed if carriage return received */
            if (receivedChar == '\r')
            {
                UART2_WriteByte('\n');
            }
        }
    }
}

void T3_Callback(uint32_t status, uintptr_t context)
{
    TMR3_Stop();    
    /* Set LED2 OFF every interrupt (every 250ms) */
    LED2_Clear();
    
}

void T2_Callback(uint32_t status, uintptr_t context)
{
    TMR3_Start(); 
    /* Timer 2 callback - triggers every 500ms - sets LED2 ON */
    static uint32_t tmr2_count = 0;
    tmr2_count++;
    
    /* Set LED2 ON every interrupt (every 500ms) */
    LED2_Set();
    
    /* Send Timer2 master message every 10 rollovers (every 5 seconds) */
    if ((tmr2_count % 10) == 0)
    {
        const char* tmr2_msg = "TMR2 500ms LED2 ON x10 (5s) - Timer3 sets LED2 OFF\r\n";
        UART2_Write((void*)tmr2_msg, strlen(tmr2_msg));
    }
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

    /* Initialize simple UART2 test instead of complex version */
    UART2_SimpleInit();

    /* LED-based diagnostic: Flash LED2 rapidly at startup to indicate UART2 init attempt */
    for (int i = 0; i < 10; i++) {
        LED2_Set();
        for (volatile int delay = 0; delay < 100000; delay++);
        LED2_Clear();
        for (volatile int delay = 0; delay < 100000; delay++);
    }

    /* Explicitly configure LED2 as output */
    LED2_OutputEnable();    /* Ensure LED2 is configured as output */
    LED2_Clear();           /* Start with LED2 OFF */

    /* Register timer callbacks and start timers */
    TMR1_CallbackRegister(T1, 0);
    TMR1_Start();
    
    /* Configure Timer2 as master timer - 500ms period */
    TMR2_CallbackRegister(T2_Callback, 0);
    TMR2_PeriodSet(39062);   /* 500ms at 50MHz with 1:64 prescaler: (500ms * 50MHz) / (1000 * 64) - 1 = 39062 */
    TMR2_Start();            /* Start Timer2 automatically */
    
    /* Configure Timer3 as slave timer - 250ms period for LED2 toggling */
    TMR3_CallbackRegister(T3_Callback, 0);
    TMR3_PeriodSet(19531);   /* 250ms at 50MHz with 1:64 prescaler: (250ms * 50MHz) / (1000 * 64) - 1 = 19531 */
               /* Start Timer3 automatically */
    
    /* Send confirmation that timers are auto-started */
    const char* timer_start_msg = "AUTO-START: TMR2(500ms LED2 ON) and TMR3(250ms LED2 OFF) started automatically!\r\n";
    UART2_SimpleWriteString(timer_start_msg);
    
    /* Add diagnostic check after UART2 init */
    if (UART2_IsEnabled()) {
        UART2_SimpleWriteString("UART2 STATUS: ENABLED\r\n");
        
        /* Add detailed register diagnostic */
        char diagnostic[25];
        UART2_DiagnosticInfo(diagnostic, sizeof(diagnostic));
        UART2_SimpleWriteString("UART2 REGS: ");
        UART2_SimpleWriteString(diagnostic);
        UART2_SimpleWriteString("\r\n");
    } else {
        /* If UART2 not enabled, flash LED2 in error pattern */
        for (int i = 0; i < 20; i++) {
            LED2_Toggle();
            for (volatile int delay = 0; delay < 50000; delay++);
        }
    }
    
    /* Register UART2 receive callback for interrupt-based reception - DISABLED FOR TEST */
    // UART2_ReadCallbackRegister(UART2_RxCallback, 0);

    /* ENABLE GLOBAL INTERRUPTS AFTER ALL INITIALIZATION */
    __builtin_enable_interrupts();  /* Enable global interrupts LAST */

    /* Send initial message via UART2 */
    const char* welcome_msg = "PIC32 UART2 TEST - 2400 BAUD - Timer2(500ms) LED2 ON & Timer3(250ms) LED2 OFF!\r\n"
                              "TMR1: 1ms (millisec counter)\r\n"
                              "TMR2: 500ms timer - sets LED2 ON\r\n"
                              "TMR3: 250ms timer - sets LED2 OFF\r\n"
                              "LED1: Toggled by main loop every 100ms\r\n"
                              "LED2: ON via TMR2(500ms), OFF via TMR3(250ms)\r\n"
                              "UART2 TEST: Send any character to test communication\r\n"
                              "Using simple polling-based UART2 on RB0(RX) and RB2(TX) at 2400 baud\r\n";
    UART2_SimpleWriteString(welcome_msg);

    uint32_t last_toggle = 0;
    uint32_t last_uart_msg = 0;
    /* uint32_t last_oc4_test = 0;  Test counter for OC4 fallback - DISABLED */
    while ( true )
    {
        /* Maintain state machines of all polled MPLAB Harmony modules. */
        if ((millisec - last_toggle) >= 100) {
            LED1_Toggle();
            last_toggle = millisec;
        }
        
        /* Simple UART2 test - echo received characters */
        if (UART2_SimpleDataAvailable())
        {
            char receivedChar = UART2_SimpleReadChar();
            
            /* Echo the character back with a message */
            UART2_SimpleWriteString("Received: ");
            UART2_SimpleWriteChar(receivedChar);
            UART2_SimpleWriteString(" (UART2 working!)\r\n");
            
            /* Handle some simple commands */
            if (receivedChar == '1')
            {
                LED2_Toggle();
                UART2_SimpleWriteString("LED2 Toggled\r\n");
            }
            else if (receivedChar == '2')
            {
                TMR2_Start();
                UART2_SimpleWriteString("TMR2 STARTED\r\n");
            }
            else if (receivedChar == 'x' || receivedChar == 'X')
            {
                TMR2_Stop();
                TMR3_Stop();
                UART2_SimpleWriteString("Timers STOPPED\r\n");
            }
        }
        
        /* Manual test - call T3 callback every 3 seconds to verify functionality */
        static uint32_t last_manual_test = 0;
        if ((millisec - last_manual_test) >= 3000) {
            T3_Callback(0, 0);  /* Manually call the Timer3 callback to test LED2 OFF */
            UART2_SimpleWriteString("MANUAL: Called T3_Callback directly - LED2 should be OFF\r\n");
            last_manual_test = millisec;
        }
        
        /* Send periodic UART message every 1000ms - INCREASED FREQUENCY FOR TESTING */
        if ((millisec - last_uart_msg) >= 1000) {
            /* Try simple single character first */
            UART2_SimpleWriteChar('A');
            UART2_SimpleWriteChar('\r');
            UART2_SimpleWriteChar('\n');
            
            /* Then try a simple string */
            UART2_SimpleWriteString("UART2 Test - millisec = ");
            
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
            
            UART2_SimpleWriteString(num_str);
            UART2_SimpleWriteString("\r\n");
            
            /* Flash LED2 briefly to indicate UART transmission attempt */
            LED2_Set();
            for (volatile int delay = 0; delay < 10000; delay++);
            LED2_Clear();
            
            last_uart_msg = millisec;
        }
    }

    /* Execution should not come here during normal operation */

    return ( EXIT_FAILURE );
}


/*******************************************************************************
 End of File
*/

