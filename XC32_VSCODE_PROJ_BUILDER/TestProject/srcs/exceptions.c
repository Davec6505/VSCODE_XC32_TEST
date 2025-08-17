/*******************************************************************************
  System Exceptions File

  File Name:
    exceptions.c

  Summary:
    Exception handlers for system exceptions.

  Description:
    This file contains exception handlers.
*******************************************************************************/

#include "definitions.h"

/* General Exception Handler */
void _general_exception_handler(void)
{
    /* Stay in infinite loop */
    while(1);
}

/* Simple TLB Refill Handler */
void _simple_tlb_refill_exception_handler(void)
{
    /* Stay in infinite loop */
    while(1);
}

/* Cache Error Exception Handler */
void _cache_err_exception_handler(void)
{
    /* Stay in infinite loop */
    while(1);
}
