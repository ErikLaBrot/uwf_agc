/*
 * Academic License - for use in teaching, academic research, and meeting
 * course requirements at degree granting institutions only.  Not for
 * government, commercial, or other organizational use.
 *
 * File: golfcart_model.h
 *
 * Code generated for Simulink model 'golfcart_model'.
 *
 * Model version                  : 1.7
 * Simulink Coder version         : 24.2 (R2024b) 21-Jun-2024
 * C/C++ source code generated on : Thu Oct  2 18:51:50 2025
 *
 * Target selection: ert.tlc
 * Embedded hardware selection: Texas Instruments->C2000
 * Code generation objectives: Unspecified
 * Validation result: Not run
 */

#ifndef golfcart_model_h_
#define golfcart_model_h_
#ifndef golfcart_model_COMMON_INCLUDES_
#define golfcart_model_COMMON_INCLUDES_
#include <string.h>
#include "rtwtypes.h"
#include "string.h"
#include "c2000BoardSupport.h"
#include "MW_f2837xD_includes.h"
#include "DSP28xx_SciUtil.h"
#include "can_message.h"
#include "F2837xD_device.h"
#include "MW_c2000DAC.h"
#endif                                 /* golfcart_model_COMMON_INCLUDES_ */

#include <stddef.h>
#include "golfcart_model_types.h"
#include "MW_target_hardware_resources.h"

/* Macros for accessing real-time model data structure */
#ifndef rtmGetErrorStatus
#define rtmGetErrorStatus(rtm)         ((rtm)->errorStatus)
#endif

#ifndef rtmSetErrorStatus
#define rtmSetErrorStatus(rtm, val)    ((rtm)->errorStatus = (val))
#endif

#ifndef rtmStepTask
#define rtmStepTask(rtm, idx)          ((rtm)->Timing.TaskCounters.TID[(idx)] == 0)
#endif

#ifndef rtmTaskCounter
#define rtmTaskCounter(rtm, idx)       ((rtm)->Timing.TaskCounters.TID[(idx)])
#endif

extern void init_eCAN_A ( uint16_T bitRatePrescaler, uint16_T timeSeg1, uint16_T
  timeSeg2, uint16_T sbg, uint16_T sjw, uint16_T sam);
extern void init_SCI(void);
extern void init_SCI_GPIO(void);

/* user code (top of export header file) */
#include "can_message.h"

/* Block signals (default storage) */
typedef struct {
  uint16_T SCIReceive[2];              /* '<S4>/SCI Receive' */
  uint16_T CANReceive_o2[8];           /* '<S1>/CAN Receive' */
  uint16_T CANReceive1_o2[8];          /* '<S1>/CAN Receive1' */
  uint16_T DataTypeConversion;         /* '<S3>/Data Type Conversion' */
  uint16_T TmpSignalConversionAtSCITransmi[4];
} B_golfcart_model_T;

/* Block states (default storage) for system '<Root>' */
typedef struct {
  codertarget_tic2000_blocks_DA_T obj; /* '<S2>/DAC' */
} DW_golfcart_model_T;

/* Real-time Model Data Structure */
struct tag_RTM_golfcart_model_T {
  const char_T * volatile errorStatus;

  /*
   * Timing:
   * The following substructure contains information regarding
   * the timing information for the model.
   */
  struct {
    struct {
      uint16_T TID[3];
    } TaskCounters;
  } Timing;
};

extern CAN_DATATYPE CAN_DATATYPE_GROUND;
extern CAN_DATATYPE CAN_DATATYPE_GROUND;
extern CAN_DATATYPE CAN_DATATYPE_GROUND;

/* Block signals (default storage) */
extern B_golfcart_model_T golfcart_model_B;

/* Block states (default storage) */
extern DW_golfcart_model_T golfcart_model_DW;

/* External function called from main */
extern void golfcart_model_SetEventsForThisBaseStep(boolean_T *eventFlags);

/* Model entry point functions */
extern void golfcart_model_initialize(void);
extern void golfcart_model_step0(void);/* Sample time: [0.0001s, 0.0s] */
extern void golfcart_model_step1(void);/* Sample time: [0.05s, 0.0s] */
extern void golfcart_model_step2(void);/* Sample time: [0.1s, 0.0s] */
extern void golfcart_model_terminate(void);

/* Real-time Model object */
extern RT_MODEL_golfcart_model_T *const golfcart_model_M;
extern volatile boolean_T stopRequested;
extern volatile boolean_T runModel;

/*-
 * These blocks were eliminated from the model due to optimizations:
 *
 * Block '<S1>/Constant' : Unused code path elimination
 * Block '<S1>/Constant1' : Unused code path elimination
 * Block '<S1>/Gain' : Unused code path elimination
 * Block '<S1>/Gain1' : Unused code path elimination
 * Block '<S1>/Sum' : Unused code path elimination
 * Block '<S1>/Sum1' : Unused code path elimination
 * Block '<S4>/Data Type Conversion' : Eliminate redundant data type conversion
 * Block '<S4>/Data Type Conversion2' : Eliminate redundant data type conversion
 * Block '<S4>/Data Type Conversion3' : Eliminate redundant data type conversion
 * Block '<S4>/Data Type Conversion4' : Eliminate redundant data type conversion
 * Block '<Root>/Constant1' : Unused code path elimination
 * Block '<S3>/Constant' : Unused code path elimination
 */

/*-
 * The generated code includes comments that allow you to trace directly
 * back to the appropriate location in the model.  The basic format
 * is <system>/block_name, where system is the system number (uniquely
 * assigned by Simulink) and block_name is the name of the block.
 *
 * Use the MATLAB hilite_system command to trace the generated code back
 * to the model.  For example,
 *
 * hilite_system('<S3>')    - opens system 3
 * hilite_system('<S3>/Kp') - opens and selects block Kp which resides in S3
 *
 * Here is the system hierarchy for this model
 *
 * '<Root>' : 'golfcart_model'
 * '<S1>'   : 'golfcart_model/kls_can_sub'
 * '<S2>'   : 'golfcart_model/kls_motor_sub'
 * '<S3>'   : 'golfcart_model/steering_sub'
 * '<S4>'   : 'golfcart_model/uart_sub'
 */
#endif                                 /* golfcart_model_h_ */

/*
 * File trailer for generated code.
 *
 * [EOF]
 */
