Fighter_UnkCallCameraCallback_8006D9EC:
/* 8006D9EC 0006A5CC  7C 08 02 A6 */	mflr r0
/* 8006D9F0 0006A5D0  90 01 00 04 */	stw r0, 4(sp)      ; point back at LR

; just as an exercise to rember ppc32 calling conventions:
; stwu is fucking weird, it does something like
;   new-sp <- sp - 0x18 ; MEM[new-sp] <- sp ; sp <- sp'
; which sets up the stack chain back-pointer
; and also allocates stack space all in one instr

/* 8006D9F4 0006A5D4  94 21 FF E8 */	stwu sp, -0x18(sp) 
/* 8006D9F8 0006A5D8  93 E1 00 14 */	stw r31, 0x14(sp)
/* 8006D9FC 0006A5DC  93 C1 00 10 */	stw r30, 0x10(sp)

; prolog over. note that r3 is first (and only) arg

/* 8006DA00 0006A5E0  7C 7E 1B 78 */	mr r30, r3           ; r30 holds FighterGObj* gobj now
/* 8006DA04 0006A5E4  83 E3 00 2C */	lwz r31, 0x2c(r3)    ; Fighter* r31/fp <- gobj.user_data
/* 8006DA08 0006A5E8  88 1F 22 1F */	lbz r0, 0x221f(r31)  ; u8 r0 <- r31/fp.x221F_b0-b7
/* 8006DA0C 0006A5EC  54 00 E7 FF */	rlwinm. r0, r0, 0x1c, 0x1f, 0x1f ; pick out b3
/* 8006DA10 0006A5F0  40 82 00 24 */	bne lbl_8006DA34     ; if (fp.x221F_b3) return;
/* 8006DA14 0006A5F4  7F C3 F3 78 */	mr r3, r30             
/* 8006DA18 0006A5F8  48 01 28 05 */	bl ftCommon_8008021C ; ftCommon_8008021C(gobj)
/* 8006DA1C 0006A5FC  81 9F 21 AC */	lwz r12, 0x21ac(r31) ; HSD_GObjEvent r12/cam_cb <- r31/fp.cam_cb
/* 8006DA20 0006A600  28 0C 00 00 */	cmplwi r12, 0
/* 8006DA24 0006A604  41 82 00 10 */	beq lbl_8006DA34     ; if (!cam_cb) return;
/* 8006DA28 0006A608  7D 88 03 A6 */	mtlr r12
/* 8006DA2C 0006A60C  38 7E 00 00 */	addi r3, r30, 0      ; put gobj in first arg. wonder why not `mr r3, r30`?
/* 8006DA30 0006A610  4E 80 00 21 */	blrl                 ; indirect cam_cb(gobj)
lbl_8006DA34:

; epilogue
/* 8006DA34 0006A614  80 01 00 1C */	lwz r0,  0x1c(sp) ; restore registers ; PATCH LANDS HERE
/* 8006DA38 0006A618  83 E1 00 14 */	lwz r31, 0x14(sp)                     ; PATCH LANDS HERE
/* 8006DA3C 0006A61C  83 C1 00 10 */	lwz r30, 0x10(sp)
/* 8006DA40 0006A620  38 21 00 18 */	addi sp, sp, 0x18 ; clear stack frame
/* 8006DA44 0006A624  7C 08 03 A6 */	mtlr r0           ; load link reg
/* 8006DA48 0006A628  4E 80 00 20 */	blr