use rust_engine::compile_pipeline;
use std::env;
use std::io::{self, Write};

fn main() {
    let args: Vec<String> = env::args().collect();

    if args.len() > 1 {
        let expression = args[1..].join(" ");
        run_compiler(&expression);
    } else {
        println!("=== Interactive Arithmetic Expression Compiler CLI ===");
        println!("Type an expression and press Enter (or 'quit' to exit):");
        loop {
            print!("\ncompiler> ");
            io::stdout().flush().unwrap();

            let mut input = String::new();
            if io::stdin().read_line(&mut input).is_err() {
                break;
            }

            let trimmed = input.trim();
            if trimmed.eq_ignore_ascii_case("quit") || trimmed.eq_ignore_ascii_case("exit") {
                println!("Exiting compiler CLI.");
                break;
            }

            if !trimmed.is_empty() {
                run_compiler(trimmed);
            }
        }
    }
}

fn run_compiler(expr: &str) {
    println!("\n========================================================");
    println!("Compiling Expression: {}", expr);
    println!("========================================================");

    let res = compile_pipeline(expr);

    if !res.success {
        println!("\n[COMPILATION FAILED]");
        if let Some(stage) = &res.error_stage {
            println!("Stage: {}", stage);
        }
        if let Some(msg) = &res.error_message {
            println!("Error: {}", msg);
        }
        if let Some(pos) = res.error_position {
            println!("Position: {}", pos);
            println!("  {}", expr);
            println!("  {}^", " ".repeat(pos));
        }
        return;
    }

    println!("\n[1] LEXICAL ANALYSIS (Tokens: {})", res.tokens.len());
    for (i, tok) in res.tokens.iter().enumerate() {
        println!("  {:2}: {:<10} | Lexeme: '{:<6}' | Span: [{}..{}]", i, tok.type_name, tok.lexeme, tok.start, tok.end);
    }

    println!("\n[2] SYNTAX ANALYSIS (AST Nodes: {}, Tree Depth: {})", res.node_count, res.tree_depth);
    if let Some(ast) = &res.ast {
        print_ast_ascii(ast, "", true);
    }

    println!("\n[3] TARGET CODE GENERATION (Stack Machine Bytecode: {})", res.bytecode.len());
    for bc in &res.bytecode {
        println!("  {:04X}: {:<12}", bc.index, bc.mnemonic);
    }

    println!("\n[4] VIRTUAL MACHINE EXECUTION (Cycles: {})", res.vm_steps.len());
    for step in &res.vm_steps {
        let stack_str = format!("{:?}", step.stack_after);
        println!("  Step {:2} [PC:{:02} | {:<8}] Stack: {:<16} | {}", step.step, step.pc, step.instruction, stack_str, step.description);
    }

    println!("\n--------------------------------------------------------");
    if let Some(val) = res.final_result {
        println!("FINAL EVALUATED RESULT: {}", val);
    }
    println!("--------------------------------------------------------");
}

fn print_ast_ascii(node: &rust_engine::ast::AstNode, prefix: &str, is_last: bool) {
    let branch = if is_last { "`-- " } else { "|-- " };
    println!("{}{}{}", prefix, branch, node.label);

    let child_prefix = format!("{}{}", prefix, if is_last { "    " } else { "|   " });
    let count = node.children.len();
    for (i, child) in node.children.iter().enumerate() {
        print_ast_ascii(child, &child_prefix, i == count - 1);
    }
}
