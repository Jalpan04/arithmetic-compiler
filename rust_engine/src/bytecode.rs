use crate::ast::{AstKind, AstNode, BinaryOp, UnaryOp};
use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub enum Opcode {
    Push(f64),
    Add,
    Sub,
    Mul,
    Div,
    Mod,
    Pow,
    Neg,
    Halt,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct BytecodeInstruction {
    pub index: usize,
    pub opcode: Opcode,
    pub mnemonic: String,
    pub operand: Option<f64>,
}

impl BytecodeInstruction {
    pub fn new(index: usize, opcode: Opcode) -> Self {
        let (mnemonic, operand) = match opcode {
            Opcode::Push(val) => (format!("PUSH {}", val), Some(val)),
            Opcode::Add => ("ADD".to_string(), None),
            Opcode::Sub => ("SUB".to_string(), None),
            Opcode::Mul => ("MUL".to_string(), None),
            Opcode::Div => ("DIV".to_string(), None),
            Opcode::Mod => ("MOD".to_string(), None),
            Opcode::Pow => ("POW".to_string(), None),
            Opcode::Neg => ("NEG".to_string(), None),
            Opcode::Halt => ("HALT".to_string(), None),
        };

        Self {
            index,
            opcode,
            mnemonic,
            operand,
        }
    }
}

pub struct BytecodeGenerator {
    instructions: Vec<BytecodeInstruction>,
}

impl BytecodeGenerator {
    pub fn new() -> Self {
        Self {
            instructions: Vec::new(),
        }
    }

    pub fn generate(mut self, root: &AstNode) -> Vec<BytecodeInstruction> {
        self.compile_node(root);
        let halt_idx = self.instructions.len();
        self.instructions.push(BytecodeInstruction::new(halt_idx, Opcode::Halt));
        self.instructions
    }

    fn compile_node(&mut self, node: &AstNode) {
        match &node.kind {
            AstKind::Number(val) => {
                let idx = self.instructions.len();
                self.instructions.push(BytecodeInstruction::new(idx, Opcode::Push(*val)));
            }
            AstKind::Unary { op, expr } => {
                self.compile_node(expr);
                let idx = self.instructions.len();
                match op {
                    UnaryOp::Negate => {
                        self.instructions.push(BytecodeInstruction::new(idx, Opcode::Neg));
                    }
                    UnaryOp::Positive => {
                        // Unary plus is a no-op on the stack
                    }
                }
            }
            AstKind::Binary { op, left, right } => {
                self.compile_node(left);
                self.compile_node(right);
                let idx = self.instructions.len();
                let bytecode_op = match op {
                    BinaryOp::Add => Opcode::Add,
                    BinaryOp::Sub => Opcode::Sub,
                    BinaryOp::Mul => Opcode::Mul,
                    BinaryOp::Div => Opcode::Div,
                    BinaryOp::Mod => Opcode::Mod,
                    BinaryOp::Pow => Opcode::Pow,
                };
                self.instructions.push(BytecodeInstruction::new(idx, bytecode_op));
            }
            AstKind::Empty => {}
        }
    }
}
