use crate::bytecode::{BytecodeInstruction, Opcode};
use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct VmStep {
    pub step: usize,
    pub pc: usize,
    pub instruction: String,
    pub stack_before: Vec<f64>,
    pub stack_after: Vec<f64>,
    pub description: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct VmExecutionReport {
    pub success: bool,
    pub final_result: Option<f64>,
    pub error: Option<String>,
    pub steps: Vec<VmStep>,
    pub total_cycles: usize,
}

pub struct VirtualMachine {
    instructions: Vec<BytecodeInstruction>,
    stack: Vec<f64>,
    pc: usize,
    steps: Vec<VmStep>,
}

impl VirtualMachine {
    pub fn new(instructions: Vec<BytecodeInstruction>) -> Self {
        Self {
            instructions,
            stack: Vec::new(),
            pc: 0,
            steps: Vec::new(),
        }
    }

    pub fn execute(&mut self) -> VmExecutionReport {
        let max_cycles = 10_000;
        let mut cycle_count = 0;

        while self.pc < self.instructions.len() && cycle_count < max_cycles {
            cycle_count += 1;
            let current_pc = self.pc;
            let opcode = self.instructions[current_pc].opcode.clone();
            let mnemonic = self.instructions[current_pc].mnemonic.clone();
            let stack_before = self.stack.clone();

            match opcode {
                Opcode::Push(val) => {
                    self.stack.push(val);
                    self.pc += 1;
                    self.record_step(
                        cycle_count,
                        current_pc,
                        &mnemonic,
                        stack_before,
                        format!("Pushed constant {} onto stack", val),
                    );
                }
                Opcode::Neg => {
                    if let Some(val) = self.stack.pop() {
                        let res = -val;
                        self.stack.push(res);
                        self.pc += 1;
                        self.record_step(
                            cycle_count,
                            current_pc,
                            &mnemonic,
                            stack_before,
                            format!("Popped {}, negated to {}, pushed result", val, res),
                        );
                    } else {
                        return self.error_report("Stack underflow during NEG operation", cycle_count);
                    }
                }
                Opcode::Add => {
                    if let (Some(b), Some(a)) = (self.stack.pop(), self.stack.pop()) {
                        let res = a + b;
                        self.stack.push(res);
                        self.pc += 1;
                        self.record_step(
                            cycle_count,
                            current_pc,
                            &mnemonic,
                            stack_before,
                            format!("Popped {} and {}, added {} + {} = {}, pushed result", b, a, a, b, res),
                        );
                    } else {
                        return self.error_report("Stack underflow during ADD operation", cycle_count);
                    }
                }
                Opcode::Sub => {
                    if let (Some(b), Some(a)) = (self.stack.pop(), self.stack.pop()) {
                        let res = a - b;
                        self.stack.push(res);
                        self.pc += 1;
                        self.record_step(
                            cycle_count,
                            current_pc,
                            &mnemonic,
                            stack_before,
                            format!("Popped {} and {}, subtracted {} - {} = {}, pushed result", b, a, a, b, res),
                        );
                    } else {
                        return self.error_report("Stack underflow during SUB operation", cycle_count);
                    }
                }
                Opcode::Mul => {
                    if let (Some(b), Some(a)) = (self.stack.pop(), self.stack.pop()) {
                        let res = a * b;
                        self.stack.push(res);
                        self.pc += 1;
                        self.record_step(
                            cycle_count,
                            current_pc,
                            &mnemonic,
                            stack_before,
                            format!("Popped {} and {}, multiplied {} * {} = {}, pushed result", b, a, a, b, res),
                        );
                    } else {
                        return self.error_report("Stack underflow during MUL operation", cycle_count);
                    }
                }
                Opcode::Div => {
                    if let (Some(b), Some(a)) = (self.stack.pop(), self.stack.pop()) {
                        if b == 0.0 {
                            return self.error_report(format!("Runtime Error: Division by zero ({} / 0)", a), cycle_count);
                        }
                        let res = a / b;
                        self.stack.push(res);
                        self.pc += 1;
                        self.record_step(
                            cycle_count,
                            current_pc,
                            &mnemonic,
                            stack_before,
                            format!("Popped {} and {}, divided {} / {} = {}, pushed result", b, a, a, b, res),
                        );
                    } else {
                        return self.error_report("Stack underflow during DIV operation", cycle_count);
                    }
                }
                Opcode::Mod => {
                    if let (Some(b), Some(a)) = (self.stack.pop(), self.stack.pop()) {
                        if b == 0.0 {
                            return self.error_report(format!("Runtime Error: Modulo by zero ({} % 0)", a), cycle_count);
                        }
                        let res = a % b;
                        self.stack.push(res);
                        self.pc += 1;
                        self.record_step(
                            cycle_count,
                            current_pc,
                            &mnemonic,
                            stack_before,
                            format!("Popped {} and {}, calculated modulo {} % {} = {}, pushed result", b, a, a, b, res),
                        );
                    } else {
                        return self.error_report("Stack underflow during MOD operation", cycle_count);
                    }
                }
                Opcode::Pow => {
                    if let (Some(b), Some(a)) = (self.stack.pop(), self.stack.pop()) {
                        let res = a.powf(b);
                        self.stack.push(res);
                        self.pc += 1;
                        self.record_step(
                            cycle_count,
                            current_pc,
                            &mnemonic,
                            stack_before,
                            format!("Popped exponent {} and base {}, evaluated {} ^ {} = {}, pushed result", b, a, a, b, res),
                        );
                    } else {
                        return self.error_report("Stack underflow during POW operation", cycle_count);
                    }
                }
                Opcode::Halt => {
                    self.record_step(
                        cycle_count,
                        current_pc,
                        &mnemonic,
                        stack_before,
                        "Execution halted normally. Top of stack is final result.".to_string(),
                    );
                    let final_val = self.stack.last().copied();
                    return VmExecutionReport {
                        success: true,
                        final_result: final_val,
                        error: None,
                        steps: self.steps.clone(),
                        total_cycles: cycle_count,
                    };
                }
            }
        }

        if cycle_count >= max_cycles {
            self.error_report("Virtual machine exceeded maximum cycle limit", cycle_count)
        } else {
            let final_val = self.stack.last().copied();
            VmExecutionReport {
                success: true,
                final_result: final_val,
                error: None,
                steps: self.steps.clone(),
                total_cycles: cycle_count,
            }
        }
    }

    fn record_step(&mut self, step: usize, pc: usize, instruction: &str, stack_before: Vec<f64>, description: String) {
        self.steps.push(VmStep {
            step,
            pc,
            instruction: instruction.to_string(),
            stack_before,
            stack_after: self.stack.clone(),
            description,
        });
    }

    fn error_report(&self, err_msg: impl Into<String>, total_cycles: usize) -> VmExecutionReport {
        VmExecutionReport {
            success: false,
            final_result: None,
            error: Some(err_msg.into()),
            steps: self.steps.clone(),
            total_cycles,
        }
    }
}
