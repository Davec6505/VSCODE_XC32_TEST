/*******************************************************************************
  System Startup File

  File Name:
    startup.S

  Summary:
    System startup code for PIC32MZ microcontrollers.
    
  Description:
    This file contains the system startup code including vector table
    and initialization routines.
*******************************************************************************/

#include <xc.h>

    .section .vector_0,code, keep
    .equ __vector_spacing_0, 0x00000001
    .align 4
    .set nomips16
    .set noreorder
    .ent __vector_0
__vector_0:
    j  _startup
    nop
    .end __vector_0
    .size __vector_0, .-__vector_0

    .section .startup,code, keep
    .align 4
    .set nomips16  
    .set noreorder
    .ent _startup
_startup:
    /* Initialize stack pointer */
    la   $sp, _stack
    
    /* Initialize global pointer */
    la   $gp, _gp
    
    /* Jump to main */
    la   $t0, main
    jr   $t0
    nop
    .end _startup
    .size _startup, .-_startup
