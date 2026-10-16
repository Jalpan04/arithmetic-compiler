pub mod ast;
pub mod bytecode;
pub mod lexer;
pub mod parser;
pub mod token;
pub mod vm;

use ast::AstNode;
use bytecode::{BytecodeGenerator, BytecodeInstruction};
use lexer::Lexer;
use parser::Parser;
use serde::{Deserialize, Serialize};
use std::ffi::{CStr, CString};
use std::os::raw::c_char;
use token::Token;
use vm::{VirtualMachine, VmStep};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CompilationResult {
    pub success: bool,
    pub input_expression: String,
    pub error_stage: Option<String>,
    pub error_message: Option<String>,
    pub error_position: Option<usize>,
    pub tokens: Vec<Token>,
    pub ast: Option<AstNode>,
    pub tree_depth: usize,
    pub node_count: usize,
    pub bytecode: Vec<BytecodeInstruction>,
    pub vm_steps: Vec<VmStep>,
    pub final_result: Option<f64>,
}

pub fn compile_pipeline(source: &str) -> CompilationResult {
    let trimmed = source.trim();

    if trimmed.is_empty() {
        return CompilationResult {
            success: false,
            input_expression: source.to_string(),
            error_stage: Some("Lexical Analysis".to_string()),
            error_message: Some("Expression is empty".to_string()),
            error_position: Some(0),
            tokens: Vec::new(),
            ast: None,
            tree_depth: 0,
            node_count: 0,
            bytecode: Vec::new(),
            vm_steps: Vec::new(),
            final_result: None,
        };
    }

    // 1. Lexical Analysis
    let mut lexer = Lexer::new(trimmed);
    let tokens = match lexer.tokenize() {
        Ok(toks) => toks,
        Err(e) => {
            return CompilationResult {
                success: false,
                input_expression: source.to_string(),
                error_stage: Some("Lexical Analysis".to_string()),
                error_message: Some(e.message),
                error_position: Some(e.position),
                tokens: Vec::new(),
                ast: None,
                tree_depth: 0,
                node_count: 0,
                bytecode: Vec::new(),
                vm_steps: Vec::new(),
                final_result: None,
            };
        }
    };

    // 2. Syntax Analysis (Pratt Parser)
    let mut parser = Parser::new(tokens.clone());
    let ast_root = match parser.parse() {
        Ok(node) => node,
        Err(e) => {
            return CompilationResult {
                success: false,
                input_expression: source.to_string(),
                error_stage: Some("Syntax Analysis (Parsing)".to_string()),
                error_message: Some(e.message),
                error_position: Some(e.start),
                tokens,
                ast: None,
                tree_depth: 0,
                node_count: 0,
                bytecode: Vec::new(),
                vm_steps: Vec::new(),
                final_result: None,
            };
        }
    };

    let tree_depth = ast_root.tree_depth();
    let node_count = ast_root.node_count();

    // 3. Target Code Generation (Stack-Machine Bytecode)
    let bc_gen = BytecodeGenerator::new();
    let bytecode = bc_gen.generate(&ast_root);

    // 4. Virtual Machine Execution
    let mut vm = VirtualMachine::new(bytecode.clone());
    let vm_report = vm.execute();

    if !vm_report.success {
        return CompilationResult {
            success: false,
            input_expression: source.to_string(),
            error_stage: Some("Runtime Execution (VM)".to_string()),
            error_message: vm_report.error,
            error_position: None,
            tokens,
            ast: Some(ast_root),
            tree_depth,
            node_count,
            bytecode,
            vm_steps: vm_report.steps,
            final_result: None,
        };
    }

    CompilationResult {
        success: true,
        input_expression: source.to_string(),
        error_stage: None,
        error_message: None,
        error_position: None,
        tokens,
        ast: Some(ast_root),
        tree_depth,
        node_count,
        bytecode,
        vm_steps: vm_report.steps,
        final_result: vm_report.final_result,
    }
}

// C-ABI Foreign Function Interface for Python ctypes
#[unsafe(no_mangle)]
pub extern "C" fn compile_expression(input_ptr: *const c_char) -> *mut c_char {
    if input_ptr.is_null() {
        let err_json = r#"{"success":false,"error_message":"Null pointer provided"}"#;
        return CString::new(err_json).unwrap().into_raw();
    }

    let c_str = unsafe { CStr::from_ptr(input_ptr) };
    let input = match c_str.to_str() {
        Ok(s) => s,
        Err(_) => {
            let err_json = r#"{"success":false,"error_message":"Invalid UTF-8 input string"}"#;
            return CString::new(err_json).unwrap().into_raw();
        }
    };

    let result = compile_pipeline(input);
    let json_str = serde_json::to_string(&result).unwrap_or_else(|e| {
        format!(r#"{{"success":false,"error_message":"JSON serialization failed: {}"}}"#, e)
    });

    CString::new(json_str).unwrap().into_raw()
}

#[unsafe(no_mangle)]
pub extern "C" fn free_string(ptr: *mut c_char) {
    if !ptr.is_null() {
        unsafe {
            let _ = CString::from_raw(ptr);
        }
    }
}
