// Lists every reference (call, jump, data) to the given addresses with the containing function.
// Arguments: <output_file> <address> [address ...]   (hex, e.g. 140322200)
// @category ER_Engine

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.symbol.Reference;

import java.io.PrintWriter;

public class FindCallers extends GhidraScript {
    @Override
    public void run() throws Exception {
        String[] args = getScriptArgs();
        try (PrintWriter w = new PrintWriter(args[0], "UTF-8")) {
            for (int i = 1; i < args.length; i++) {
                Address target = toAddr(Long.parseUnsignedLong(args[i], 16));
                w.println("== " + target);
                for (Reference r : getReferencesTo(target)) {
                    Address from = r.getFromAddress();
                    Function f = getFunctionContaining(from);
                    w.println(from + "\t" + r.getReferenceType() + "\t" + (f == null ? "?" : f.getName() + "@" + f.getEntryPoint()));
                }
            }
        }
    }
}
