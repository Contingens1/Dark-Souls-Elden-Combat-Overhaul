// Linear disassembly of address ranges (in memory only; the project is opened read-only, nothing is saved).
// For code Ghidra could not reach on its own, e.g. a function whose entry jumps into a protection stub
// outside the image. Prints address, bytes and instruction text.
// Arguments: <output_file> <start> <end> [<start> <end> ...]   (hex, e.g. 140328130 140328273)
// @category ER_Engine
import ghidra.app.cmd.disassemble.DisassembleCommand;
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.address.AddressSet;
import ghidra.program.model.listing.Instruction;
import java.io.PrintWriter;

public class DisasmRange extends GhidraScript {
    @Override
    public void run() throws Exception {
        String[] args = getScriptArgs();
        try (PrintWriter w = new PrintWriter(args[0], "UTF-8")) {
            for (int i = 1; i + 1 < args.length; i += 2) {
                Address start = toAddr(Long.parseUnsignedLong(args[i], 16));
                Address end = toAddr(Long.parseUnsignedLong(args[i + 1], 16));
                w.println("== " + start + " - " + end);
                Address a = start;
                while (a.compareTo(end) < 0) {
                    Instruction ins = getInstructionAt(a);
                    if (ins == null) {
                        clearListing(a, a);
                        DisassembleCommand cmd = new DisassembleCommand(new AddressSet(a, a), null, false);
                        cmd.applyTo(currentProgram, monitor);
                        ins = getInstructionAt(a);
                    }
                    if (ins == null) {
                        w.println(a + "\t??\t" + String.format("%02X", getByte(a) & 0xFF));
                        a = a.add(1);
                        continue;
                    }
                    StringBuilder hex = new StringBuilder();
                    for (byte b : ins.getBytes()) hex.append(String.format("%02X", b & 0xFF));
                    w.println(a + "\t" + hex + "\t" + ins);
                    a = a.add(ins.getLength());
                }
            }
        }
        println("DisasmRange done");
    }
}
