// Lists the game's input-query functions in an address range (the "action N pressed / held" family around
// FUN_1401a46b0, roll pressed = action 0x5C): for each function the action ids its decompiled body asks for
// (vtable+0x88 call or FUN_1401a5ca0(ctx, id)), the bit it falls back to, and its callers. Read-only.
// Arguments: <output_file> <hex start> <hex end>
// @category ER_Engine
import ghidra.app.decompiler.*;
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionIterator;
import ghidra.program.model.symbol.Reference;
import java.io.PrintWriter;
import java.util.*;
import java.util.regex.*;

public class ActionQueryFuncs extends GhidraScript {
    private static final Pattern ACT = Pattern.compile("(?:\\+ 0x88\\)\\)\\(|FUN_1401a5ca0\\([^,]+,|FUN_1401a5[0-9a-f]{3}\\([^,]+,)(0x[0-9a-f]+|\\d+)");
    private static final Pattern BIT = Pattern.compile("\\+ 0x50\\) \\+ (\\d+|0x[0-9a-f]+)\\) >> (0x[0-9a-f]+|\\d+)");

    @Override
    public void run() throws Exception {
        String[] args = getScriptArgs();
        Address a0 = toAddr(Long.parseUnsignedLong(args[1], 16)), a1 = toAddr(Long.parseUnsignedLong(args[2], 16));
        DecompInterface dec = new DecompInterface();
        dec.openProgram(currentProgram);
        try (PrintWriter w = new PrintWriter(args[0], "UTF-8")) {
            FunctionIterator it = currentProgram.getFunctionManager().getFunctions(a0, true);
            while (it.hasNext()) {
                Function f = it.next();
                if (f.getEntryPoint().compareTo(a1) >= 0) break;
                DecompileResults dr = dec.decompileFunction(f, 60, monitor);
                if (!dr.decompileCompleted()) continue;
                String c = dr.getDecompiledFunction().getC();
                List<String> ids = new ArrayList<>();
                Matcher m = ACT.matcher(c);
                while (m.find()) ids.add(m.group(1));
                List<String> bits = new ArrayList<>();
                Matcher b = BIT.matcher(c);
                while (b.find()) bits.add("+" + b.group(1) + ">>" + b.group(2));
                List<String> calls = new ArrayList<>();
                Matcher cm = Pattern.compile("FUN_1401a[0-9a-f]{4}").matcher(c);
                while (cm.find()) if (!cm.group().equals("FUN_" + f.getEntryPoint().toString().substring(0))) calls.add(cm.group());
                Set<String> callers = new TreeSet<>();
                for (Reference r : getReferencesTo(f.getEntryPoint())) {
                    Function cf = getFunctionContaining(r.getFromAddress());
                    if (r.getReferenceType().isCall()) callers.add((cf != null ? cf.getEntryPoint().toString() : "?") + "@" + r.getFromAddress());
                    else if (!r.getReferenceType().isFlow()) callers.add("data@" + r.getFromAddress());
                }
                w.println(String.format("%s  len %4d  actions [%s]  bits [%s]  uses [%s]", f.getEntryPoint(), f.getBody().getNumAddresses(),
                        String.join(",", ids), String.join(",", bits), String.join(",", new LinkedHashSet<>(calls))));
                if (!callers.isEmpty()) w.println("      callers " + String.join(" ", callers));
            }
        }
        dec.dispose();
    }
}
