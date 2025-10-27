/*
 * Academic License - for use in teaching, academic research, and meeting
 * course requirements at degree granting institutions only.  Not for
 * government, commercial, or other organizational use.
 *
 * File: golfcart_model.c
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

#include "golfcart_model.h"
#include "rtwtypes.h"
#include "golfcart_model_private.h"
#include <math.h>
#include <string.h>

/* Block signals (default storage) */
B_golfcart_model_T golfcart_model_B;

/* Block states (default storage) */
DW_golfcart_model_T golfcart_model_DW;

/* Real-time model */
static RT_MODEL_golfcart_model_T golfcart_model_M_;
RT_MODEL_golfcart_model_T *const golfcart_model_M = &golfcart_model_M_;
static void rate_monotonic_scheduler(void);

/*
 * Set which subrates need to run this base step (base rate always runs).
 * This function must be called prior to calling the model step function
 * in order to remember which rates need to run this base step.  The
 * buffering of events allows for overlapping preemption.
 */
void golfcart_model_SetEventsForThisBaseStep(boolean_T *eventFlags)
{
  /* Task runs when its counter is zero, computed via rtmStepTask macro */
  eventFlags[1] = ((boolean_T)rtmStepTask(golfcart_model_M, 1));
  eventFlags[2] = ((boolean_T)rtmStepTask(golfcart_model_M, 2));
}

/*
 *         This function updates active task flag for each subrate
 *         and rate transition flags for tasks that exchange data.
 *         The function assumes rate-monotonic multitasking scheduler.
 *         The function must be called at model base rate so that
 *         the generated code self-manages all its subrates and rate
 *         transition flags.
 */
static void rate_monotonic_scheduler(void)
{
  /* Compute which subrates run during the next base time step.  Subrates
   * are an integer multiple of the base rate counter.  Therefore, the subtask
   * counter is reset when it reaches its limit (zero means run).
   */
  (golfcart_model_M->Timing.TaskCounters.TID[1])++;
  if ((golfcart_model_M->Timing.TaskCounters.TID[1]) > 499) {/* Sample time: [0.05s, 0.0s] */
    golfcart_model_M->Timing.TaskCounters.TID[1] = 0;
  }

  (golfcart_model_M->Timing.TaskCounters.TID[2])++;
  if ((golfcart_model_M->Timing.TaskCounters.TID[2]) > 999) {/* Sample time: [0.1s, 0.0s] */
    golfcart_model_M->Timing.TaskCounters.TID[2] = 0;
  }
}

real_T rt_roundd_snf(real_T u)
{
  real_T y;
  if (fabs(u) < 4.503599627370496E+15) {
    if (u >= 0.5) {
      y = floor(u + 0.5);
    } else if (u > -0.5) {
      y = u * 0.0;
    } else {
      y = ceil(u - 0.5);
    }
  } else {
    y = u;
  }

  return y;
}

/* Model step function for TID0 */
void golfcart_model_step0(void)        /* Sample time: [0.0001s, 0.0s] */
{
  {                                    /* Sample time: [0.0001s, 0.0s] */
    rate_monotonic_scheduler();
  }
}

/* Model step function for TID1 */
void golfcart_model_step1(void)        /* Sample time: [0.05s, 0.0s] */
{
  /* local block i/o variables */
  uint16_T rtb_MSG1ToBytes_o2;
  uint16_T rtb_MSG1ToBytes_o3;
  uint16_T rtb_MSG1ToBytes_o4;
  uint16_T rtb_MSG2ToBytes_o1;
  uint16_T rtb_MSG2ToBytes_o2;
  uint16_T rtb_MSG2ToBytes_o3;
  uint16_T rtb_MSG2ToBytes_o4;
  uint16_T rtb_MSG2ToBytes_o5;
  uint16_T rtb_MSG2ToBytes_o6;
  uint16_T rtb_MSG2ToBytes_o7;
  uint16_T rtb_MSG2ToBytes_o8;
  uint16_T rtb_BytePack[2];
  uint16_T rtb_MSG1ToBytes_o1;

  /* S-Function (c280xcanrcv): '<S1>/CAN Receive' */
  {
    uchar_T ucRXMsgData[8]= { 0, 0, 0, 0, 0, 0, 0, 0 };

    uint16_T status = 0;
    CAN_MsgFrameType frameType;
    uint32_T messageID = 0;
    uint32_T reqNewDataRegValue = (((uint32_T)0x1)<<0);
    uint32_T newDataReg = CAN_getNewDataFlags(CANA_BASE) & reqNewDataRegValue;
    if (newDataReg == reqNewDataRegValue) {
      status = CAN_readMessageWithID(CANA_BASE, 1, &frameType, &messageID,
        (uint16_T*)ucRXMsgData);
    }

    if ((newDataReg == reqNewDataRegValue)&&(status > 0)) {
      golfcart_model_B.CANReceive_o2[0] = ucRXMsgData[0];
      golfcart_model_B.CANReceive_o2[1] = ucRXMsgData[1];
      golfcart_model_B.CANReceive_o2[2] = ucRXMsgData[2];
      golfcart_model_B.CANReceive_o2[3] = ucRXMsgData[3];
      golfcart_model_B.CANReceive_o2[4] = ucRXMsgData[4];
      golfcart_model_B.CANReceive_o2[5] = ucRXMsgData[5];
      golfcart_model_B.CANReceive_o2[6] = ucRXMsgData[6];
      golfcart_model_B.CANReceive_o2[7] = ucRXMsgData[7];

      /* -- Call CAN RX Fcn-Call_0 -- */
    }
  }

  /* S-Function (byte2any_svd): '<S1>/MSG1 To Bytes' */

  /* Unpack: <S1>/MSG1 To Bytes */
  {
    uint32_T MW_inputPortOffset = 0U;
    uint16_T MW_outputPortWidth = 0U;

    /* Packed input data type - uint16_T */
    void* unpackData = &golfcart_model_B.CANReceive_o2[0];

    /* Unpacking the values to output 1 */
    /* Output data type - uint16_T, size - 1 */
    {
      MW_outputPortWidth = (uint16_T)2 * sizeof(uint16_T);
      uint16_T* MW_pTmp20 = &(((uint16_T *)unpackData)[MW_inputPortOffset]);
      uint16_T MW_idx2 = 0U;
      uint16_T MW_tmp2[8];
      for (MW_idx2 = 0; MW_idx2 < (MW_outputPortWidth/2); MW_idx2++) {
        MW_tmp2[MW_idx2] = (uint16_T)((uint16_T)(MW_pTmp20[(2*MW_idx2)]) &
          0x00FFU);
        MW_tmp2[MW_idx2] |= (uint16_T)(((uint16_T)(MW_pTmp20[((2*MW_idx2)+1)]) &
          0x00FFU) << 8U);
      }

      memcpy((void*)&rtb_MSG1ToBytes_o1, (void*)&MW_tmp2[0], (MW_outputPortWidth/
              2));
    }

    /* Offset calculations based on alignment for packing next input */
    MW_inputPortOffset = MW_inputPortOffset + MW_outputPortWidth;

    /* Unpacking the values to output 2 */
    /* Output data type - uint16_T, size - 1 */
    {
      MW_outputPortWidth = (uint16_T)2 * sizeof(uint16_T);
      uint16_T* MW_pTmp21 = &(((uint16_T *)unpackData)[MW_inputPortOffset]);
      uint16_T MW_idx2 = 0U;
      uint16_T MW_tmp2[8];
      for (MW_idx2 = 0; MW_idx2 < (MW_outputPortWidth/2); MW_idx2++) {
        MW_tmp2[MW_idx2] = (uint16_T)((uint16_T)(MW_pTmp21[(2*MW_idx2)]) &
          0x00FFU);
        MW_tmp2[MW_idx2] |= (uint16_T)(((uint16_T)(MW_pTmp21[((2*MW_idx2)+1)]) &
          0x00FFU) << 8U);
      }

      memcpy((void*)&rtb_MSG1ToBytes_o2, (void*)&MW_tmp2[0], (MW_outputPortWidth/
              2));
    }

    /* Offset calculations based on alignment for packing next input */
    MW_inputPortOffset = MW_inputPortOffset + MW_outputPortWidth;

    /* Unpacking the values to output 3 */
    /* Output data type - uint16_T, size - 1 */
    {
      MW_outputPortWidth = (uint16_T)2 * sizeof(uint16_T);
      uint16_T* MW_pTmp22 = &(((uint16_T *)unpackData)[MW_inputPortOffset]);
      uint16_T MW_idx2 = 0U;
      uint16_T MW_tmp2[8];
      for (MW_idx2 = 0; MW_idx2 < (MW_outputPortWidth/2); MW_idx2++) {
        MW_tmp2[MW_idx2] = (uint16_T)((uint16_T)(MW_pTmp22[(2*MW_idx2)]) &
          0x00FFU);
        MW_tmp2[MW_idx2] |= (uint16_T)(((uint16_T)(MW_pTmp22[((2*MW_idx2)+1)]) &
          0x00FFU) << 8U);
      }

      memcpy((void*)&rtb_MSG1ToBytes_o3, (void*)&MW_tmp2[0], (MW_outputPortWidth/
              2));
    }

    /* Offset calculations based on alignment for packing next input */
    MW_inputPortOffset = MW_inputPortOffset + MW_outputPortWidth;

    /* Unpacking the values to output 4 */
    /* Output data type - uint16_T, size - 1 */
    {
      MW_outputPortWidth = (uint16_T)2 * sizeof(uint16_T);
      uint16_T* MW_pTmp23 = &(((uint16_T *)unpackData)[MW_inputPortOffset]);
      uint16_T MW_idx2 = 0U;
      uint16_T MW_tmp2[8];
      for (MW_idx2 = 0; MW_idx2 < (MW_outputPortWidth/2); MW_idx2++) {
        MW_tmp2[MW_idx2] = (uint16_T)((uint16_T)(MW_pTmp23[(2*MW_idx2)]) &
          0x00FFU);
        MW_tmp2[MW_idx2] |= (uint16_T)(((uint16_T)(MW_pTmp23[((2*MW_idx2)+1)]) &
          0x00FFU) << 8U);
      }

      memcpy((void*)&rtb_MSG1ToBytes_o4, (void*)&MW_tmp2[0], (MW_outputPortWidth/
              2));
    }
  }

  /* S-Function (c280xcanrcv): '<S1>/CAN Receive1' */
  {
    uchar_T ucRXMsgData[8]= { 0, 0, 0, 0, 0, 0, 0, 0 };

    uint16_T status = 0;
    CAN_MsgFrameType frameType;
    uint32_T messageID = 0;
    uint32_T reqNewDataRegValue = (((uint32_T)0x1)<<1);
    uint32_T newDataReg = CAN_getNewDataFlags(CANA_BASE) & reqNewDataRegValue;
    if (newDataReg == reqNewDataRegValue) {
      status = CAN_readMessageWithID(CANA_BASE, 2, &frameType, &messageID,
        (uint16_T*)ucRXMsgData);
    }

    if ((newDataReg == reqNewDataRegValue)&&(status > 0)) {
      golfcart_model_B.CANReceive1_o2[0] = ucRXMsgData[0];
      golfcart_model_B.CANReceive1_o2[1] = ucRXMsgData[1];
      golfcart_model_B.CANReceive1_o2[2] = ucRXMsgData[2];
      golfcart_model_B.CANReceive1_o2[3] = ucRXMsgData[3];
      golfcart_model_B.CANReceive1_o2[4] = ucRXMsgData[4];
      golfcart_model_B.CANReceive1_o2[5] = ucRXMsgData[5];
      golfcart_model_B.CANReceive1_o2[6] = ucRXMsgData[6];
      golfcart_model_B.CANReceive1_o2[7] = ucRXMsgData[7];

      /* -- Call CAN RX Fcn-Call_0 -- */
    }
  }

  /* S-Function (byte2any_svd): '<S1>/MSG2 To Bytes' */

  /* Unpack: <S1>/MSG2 To Bytes */
  {
    uint32_T MW_inputPortOffset = 0U;
    uint16_T MW_outputPortWidth = 0U;

    /* Packed input data type - uint16_T */
    void* unpackData = &golfcart_model_B.CANReceive1_o2[0];

    /* Unpacking the values to output 1 */
    /* Output data type - uint16_T, size - 1 */
    {
      MW_outputPortWidth = (uint16_T)1 * sizeof(uint16_T);
      memcpy((void*)&rtb_MSG2ToBytes_o1, (void *)&(((uint16_T *)unpackData)
              [MW_inputPortOffset]), MW_outputPortWidth);
    }

    /* Offset calculations based on alignment for packing next input */
    MW_inputPortOffset = MW_inputPortOffset + MW_outputPortWidth;

    /* Unpacking the values to output 2 */
    /* Output data type - uint16_T, size - 1 */
    {
      MW_outputPortWidth = (uint16_T)1 * sizeof(uint16_T);
      memcpy((void*)&rtb_MSG2ToBytes_o2, (void *)&(((uint16_T *)unpackData)
              [MW_inputPortOffset]), MW_outputPortWidth);
    }

    /* Offset calculations based on alignment for packing next input */
    MW_inputPortOffset = MW_inputPortOffset + MW_outputPortWidth;

    /* Unpacking the values to output 3 */
    /* Output data type - uint16_T, size - 1 */
    {
      MW_outputPortWidth = (uint16_T)1 * sizeof(uint16_T);
      memcpy((void*)&rtb_MSG2ToBytes_o3, (void *)&(((uint16_T *)unpackData)
              [MW_inputPortOffset]), MW_outputPortWidth);
    }

    /* Offset calculations based on alignment for packing next input */
    MW_inputPortOffset = MW_inputPortOffset + MW_outputPortWidth;

    /* Unpacking the values to output 4 */
    /* Output data type - uint16_T, size - 1 */
    {
      MW_outputPortWidth = (uint16_T)1 * sizeof(uint16_T);
      memcpy((void*)&rtb_MSG2ToBytes_o4, (void *)&(((uint16_T *)unpackData)
              [MW_inputPortOffset]), MW_outputPortWidth);
    }

    /* Offset calculations based on alignment for packing next input */
    MW_inputPortOffset = MW_inputPortOffset + MW_outputPortWidth;

    /* Unpacking the values to output 5 */
    /* Output data type - uint16_T, size - 1 */
    {
      MW_outputPortWidth = (uint16_T)1 * sizeof(uint16_T);
      memcpy((void*)&rtb_MSG2ToBytes_o5, (void *)&(((uint16_T *)unpackData)
              [MW_inputPortOffset]), MW_outputPortWidth);
    }

    /* Offset calculations based on alignment for packing next input */
    MW_inputPortOffset = MW_inputPortOffset + MW_outputPortWidth;

    /* Unpacking the values to output 6 */
    /* Output data type - uint16_T, size - 1 */
    {
      MW_outputPortWidth = (uint16_T)1 * sizeof(uint16_T);
      memcpy((void*)&rtb_MSG2ToBytes_o6, (void *)&(((uint16_T *)unpackData)
              [MW_inputPortOffset]), MW_outputPortWidth);
    }

    /* Offset calculations based on alignment for packing next input */
    MW_inputPortOffset = MW_inputPortOffset + MW_outputPortWidth;

    /* Unpacking the values to output 7 */
    /* Output data type - uint16_T, size - 1 */
    {
      MW_outputPortWidth = (uint16_T)1 * sizeof(uint16_T);
      memcpy((void*)&rtb_MSG2ToBytes_o7, (void *)&(((uint16_T *)unpackData)
              [MW_inputPortOffset]), MW_outputPortWidth);
    }

    /* Offset calculations based on alignment for packing next input */
    MW_inputPortOffset = MW_inputPortOffset + MW_outputPortWidth;

    /* Unpacking the values to output 8 */
    /* Output data type - uint16_T, size - 1 */
    {
      MW_outputPortWidth = (uint16_T)1 * sizeof(uint16_T);
      memcpy((void*)&rtb_MSG2ToBytes_o8, (void *)&(((uint16_T *)unpackData)
              [MW_inputPortOffset]), MW_outputPortWidth);
    }
  }

  /* S-Function (any2byte_svd): '<S4>/Byte Pack' */

  /* Pack: <S4>/Byte Pack */
  {
    uint32_T MW_outputPortOffset = 0U;
    uint16_T MW_inputPortWidth = 0U;

    /* Packed output data type - uint16_T */
    void* packData = &rtb_BytePack[0];

    /* Packing the values of Input 1 */
    /* Input data type - uint16_T, size - 1 */
    {
      MW_inputPortWidth = (uint16_T)2U * sizeof(uint16_T);
      uint16_T* MW_pTmp10 = (uint16_T*)&rtb_MSG1ToBytes_o1;
      uint16_T MW_idx1 = 0U;
      uint16_T MW_tmp1[2];
      for (MW_idx1 = 0U; MW_idx1 < (MW_inputPortWidth/2U); MW_idx1++) {
        MW_tmp1[2*MW_idx1] = (uint16_T)((uint16_T)(MW_pTmp10[MW_idx1]) & 0x00FF);
        MW_tmp1[(2*MW_idx1)+1] = (uint16_T)(((uint16_T)(MW_pTmp10[MW_idx1]) &
          0xFF00) >> 8);
      }

      memcpy((void *)&(((uint16_T *)packData)[MW_outputPortOffset]), (void*)
             &MW_tmp1[0], MW_inputPortWidth);
    }
  }

  /* SignalConversion generated from: '<S4>/SCI Transmit' incorporates:
   *  Constant: '<S4>/Constant'
   */
  golfcart_model_B.TmpSignalConversionAtSCITransmi[0] = 255U;
  golfcart_model_B.TmpSignalConversionAtSCITransmi[1] = rtb_BytePack[0];
  golfcart_model_B.TmpSignalConversionAtSCITransmi[2] = rtb_BytePack[1];
  golfcart_model_B.TmpSignalConversionAtSCITransmi[3] = 0U;

  /* S-Function (c28xsci_tx): '<S4>/SCI Transmit' */
  {
    if (frameA2Transmitted) {
      frameA1Transmitted = 0U;
      if (checkSCITransmitInProgressA != 1U) {
        checkSCITransmitInProgressA = 1U;
        int16_T errFlgHeader = NOERROR;
        int16_T errFlgData = NOERROR;
        int16_T errFlgTail = NOERROR;
        if (frameA1Count == 0) {
          errFlgData = scia_xmit((uchar_T*)
            &golfcart_model_B.TmpSignalConversionAtSCITransmi[0], 4, 1);
          frameA1Count = frameA1Count + 1U;
          checkSCITransmitInProgressA = 0U;
        } else if (frameA1Count == (3U-1)) {
          errFlgData = scia_xmit((uchar_T*)
            &golfcart_model_B.TmpSignalConversionAtSCITransmi[0], 4, 1);
          frameA1Count = 0U;
          checkSCITransmitInProgressA = 0U;
          frameA1Transmitted = 1U;
        } else {
          errFlgData = scia_xmit((uchar_T*)
            &golfcart_model_B.TmpSignalConversionAtSCITransmi[0], 4, 1);
          frameA1Count = frameA1Count + 1U;
          checkSCITransmitInProgressA = 0U;
        }
      }
    }
  }
}

/* Model step function for TID2 */
void golfcart_model_step2(void)        /* Sample time: [0.1s, 0.0s] */
{
  real_T tmp;
  int16_T rtb_Saturation1;
  uint16_T tmp_0;

  /* S-Function (c28xsci_rx): '<S4>/SCI Receive' */
  {
    int16_T i;
    int16_T errFlg = NOERROR;
    uint16_T isHeadReceived = 1U;
    uint16_T recbuff[2];
    for (i = 0; i < 2; i++) {
      recbuff[i] = 0U;
    }

    errFlg = NOERROR;

    /* Receiving data: For uint32 and uint16, rcvBuff will contain uint16 data */
    if (isHeadReceived) {
      errFlg = scia_rcv(recbuff, 2, 1);
      asm(" NOP");
      if ((errFlg == NOERROR) || (errFlg == PARTIALDATA)) {
        memcpy( &golfcart_model_B.SCIReceive[0], recbuff, 2);
      }
    }
  }

  /* DataTypeConversion: '<S4>/Data Type Conversion1' */
  rtb_Saturation1 = (golfcart_model_B.SCIReceive[1] & 128U) != 0U ? (int16_T)
    golfcart_model_B.SCIReceive[1] | -128 : (int16_T)
    (golfcart_model_B.SCIReceive[1] & 127U);

  /* Saturate: '<S3>/Saturation1' */
  if (rtb_Saturation1 > 1) {
    rtb_Saturation1 = 1;
  } else if (rtb_Saturation1 < -1) {
    rtb_Saturation1 = -1;
  }

  /* End of Saturate: '<S3>/Saturation1' */

  /* DeadZone: '<S3>/Dead Zone' incorporates:
   *  Saturate: '<S3>/Saturation1'
   */
  if (rtb_Saturation1 > 0) {
    rtb_Saturation1 = 1;

    /* Switch: '<S3>/Switch' incorporates:
     *  Constant: '<S3>/Constant1'
     *  DeadZone: '<S3>/Dead Zone'
     *  Gain: '<S3>/Gain'
     *  Sum: '<S3>/Add'
     */
    tmp = 126.0 * (real_T)rtb_Saturation1 * 0.5 + 64.0;
  } else if (rtb_Saturation1 >= 0) {
    rtb_Saturation1 = 0;

    /* Switch: '<S3>/Switch' incorporates:
     *  Constant: '<S3>/Constant1'
     *  DeadZone: '<S3>/Dead Zone'
     *  Gain: '<S3>/Gain'
     *  Sum: '<S3>/Add'
     */
    tmp = 126.0 * (real_T)rtb_Saturation1 * 0.5 + 64.0;
  } else {
    /* Switch: '<S3>/Switch' incorporates:
     *  Constant: '<S3>/Constant1'
     *  Gain: '<S3>/Gain1'
     *  Sum: '<S3>/Subtract'
     */
    tmp = 127.0;
  }

  /* End of DeadZone: '<S3>/Dead Zone' */

  /* DataTypeConversion: '<S3>/Data Type Conversion' incorporates:
   *  Switch: '<S3>/Switch'
   */
  golfcart_model_B.DataTypeConversion = (uint16_T)rt_roundd_snf(tmp);

  /* S-Function (c28xsci_tx): '<S3>/SCI Transmit' */
  {
    if (frameA1Transmitted) {
      frameA2Transmitted = 0U;
      if (checkSCITransmitInProgressA != 1U) {
        checkSCITransmitInProgressA = 1U;
        int16_T errFlgHeader = NOERROR;
        int16_T errFlgData = NOERROR;
        int16_T errFlgTail = NOERROR;
        frameA2Transmitted = 0U;

        /* Send additional data header */
        {
          uchar_T *String = "S";
          errFlgHeader = scia_xmit(String, 1, 1);
        }

        errFlgData = scia_xmit((uchar_T*)&golfcart_model_B.DataTypeConversion, 1,
          1);

        /* Send additional data terminator */
        {
          uchar_T *String = "E";
          errFlgTail = scia_xmit(String, 1, 1);
        }

        frameA2Transmitted = 1U;
        checkSCITransmitInProgressA = 0U;
      }
    }
  }

  /* Saturate: '<S2>/[0,100]' incorporates:
   *  Switch: '<S2>/Switch'
   */
  if (golfcart_model_B.SCIReceive[0] <= 100U) {
    tmp_0 = golfcart_model_B.SCIReceive[0];
  } else {
    tmp_0 = 100U;
  }

  /* DataTypeConversion: '<S2>/Data Type Conversion' incorporates:
   *  DataTypeConversion: '<S2>/Data Type Conversion1'
   *  Gain: '<S2>/40.95'
   *  Saturate: '<S2>/[0,100]'
   *  Switch: '<S2>/Switch'
   */
  rtb_Saturation1 = (int16_T)(real32_T)fmod((int16_T)(41U * tmp_0), 65536.0);

  /* Saturate: '<S2>/[0,4095]' incorporates:
   *  DataTypeConversion: '<S2>/Data Type Conversion'
   *  Switch: '<S2>/Switch'
   */
  if ((uint16_T)rtb_Saturation1 <= 4095U) {
    tmp_0 = (uint16_T)rtb_Saturation1;
  } else {
    tmp_0 = 4095U;
  }

  /* MATLABSystem: '<S2>/DAC' incorporates:
   *  Saturate: '<S2>/[0,4095]'
   *  Switch: '<S2>/Switch'
   */
  MW_C2000DACSat(0U, (real_T)(int16_T)tmp_0);
}

/* Model initialize function */
void golfcart_model_initialize(void)
{
  /* Registration code */

  /* initialize real-time model */
  (void) memset((void *)golfcart_model_M, 0,
                sizeof(RT_MODEL_golfcart_model_T));

  /* block I/O */
  (void) memset(((void *) &golfcart_model_B), 0,
                sizeof(B_golfcart_model_T));

  /* states (dwork) */
  (void) memset((void *)&golfcart_model_DW, 0,
                sizeof(DW_golfcart_model_T));

  /* Start for S-Function (c28xsci_rx): '<S4>/SCI Receive' */

  /* Initialize out port */
  {
    golfcart_model_B.SCIReceive[0] = (uint16_T)0.0;
    golfcart_model_B.SCIReceive[1] = (uint16_T)0.0;
  }

  /* Start for S-Function (c280xcanrcv): '<S1>/CAN Receive' */
  {
    uint32_T ui32Flags;
    ui32Flags = CAN_MSG_OBJ_NO_FLAGS;
    CAN_setupMessageObject(CANA_BASE, 1, 0xCF11E05, CAN_MSG_FRAME_EXT,
      CAN_MSG_OBJ_TYPE_RX, 0, ui32Flags, sizeof(uchar_T) * 8);
  }

  /* Initialize out port */
  {
    golfcart_model_B.CANReceive_o2[0] = (uint16_T)0.0;
    golfcart_model_B.CANReceive_o2[1] = (uint16_T)0.0;
    golfcart_model_B.CANReceive_o2[2] = (uint16_T)0.0;
    golfcart_model_B.CANReceive_o2[3] = (uint16_T)0.0;
    golfcart_model_B.CANReceive_o2[4] = (uint16_T)0.0;
    golfcart_model_B.CANReceive_o2[5] = (uint16_T)0.0;
    golfcart_model_B.CANReceive_o2[6] = (uint16_T)0.0;
    golfcart_model_B.CANReceive_o2[7] = (uint16_T)0.0;
  }

  /* Start for S-Function (c280xcanrcv): '<S1>/CAN Receive1' */
  {
    uint32_T ui32Flags;
    ui32Flags = CAN_MSG_OBJ_NO_FLAGS;
    CAN_setupMessageObject(CANA_BASE, 2, 0xCF11F05, CAN_MSG_FRAME_EXT,
      CAN_MSG_OBJ_TYPE_RX, 0, ui32Flags, sizeof(uchar_T) * 8);
  }

  /* Initialize out port */
  {
    golfcart_model_B.CANReceive1_o2[0] = (uint16_T)0.0;
    golfcart_model_B.CANReceive1_o2[1] = (uint16_T)0.0;
    golfcart_model_B.CANReceive1_o2[2] = (uint16_T)0.0;
    golfcart_model_B.CANReceive1_o2[3] = (uint16_T)0.0;
    golfcart_model_B.CANReceive1_o2[4] = (uint16_T)0.0;
    golfcart_model_B.CANReceive1_o2[5] = (uint16_T)0.0;
    golfcart_model_B.CANReceive1_o2[6] = (uint16_T)0.0;
    golfcart_model_B.CANReceive1_o2[7] = (uint16_T)0.0;
  }

  /* Start for MATLABSystem: '<S2>/DAC' */
  golfcart_model_DW.obj.matlabCodegenIsDeleted = false;
  golfcart_model_DW.obj.isInitialized = 1L;
  MW_ConfigureDACA();
  golfcart_model_DW.obj.isSetupComplete = true;
}

/* Model terminate function */
void golfcart_model_terminate(void)
{
  /* Terminate for MATLABSystem: '<S2>/DAC' */
  if (!golfcart_model_DW.obj.matlabCodegenIsDeleted) {
    golfcart_model_DW.obj.matlabCodegenIsDeleted = true;
  }

  /* End of Terminate for MATLABSystem: '<S2>/DAC' */
}

/*
 * File trailer for generated code.
 *
 * [EOF]
 */
