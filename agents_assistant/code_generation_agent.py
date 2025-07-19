from .agent_base import AgentBase

class CodeGenerationAgent(AgentBase):
    async def handle(self, message):
        structured = message["payload"]["structured"]
        func = structured['entities'].get('function_name', 'foo')
        lang = structured['entities'].get('language', 'python').lower()
        if lang == "python":
            code = f"def {func}():\n    pass\n# Langage: python"
            file_path = f"{func}.py"
        elif lang in ("js", "javascript"):
            code = f"function {func}() {{\n    // TODO\n}}\n// Langage: JavaScript"
            file_path = f"{func}.js"
        elif lang == "java":
            code = f"public class {func.capitalize()} {{\n    public static void {func}() {{\n        // TODO\n    }}\n}}\n// Langage: Java"
            file_path = f"{func}.java"
        else:
            code = f"void {func}() {{\n    // TODO\n}}\n// Langage: C/C++"
            file_path = f"{func}.cpp"
        await self.send("CodeImplementationAgent", {"code": code, "meta": {**structured, "file_path": file_path}})
