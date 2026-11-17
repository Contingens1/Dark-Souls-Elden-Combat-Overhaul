// Lists switch statements that have all the given cases (Ghidra labels switchD_<addr>::caseD_<hex>), with the number
// of cases and the function holding them. Used to find the ESD environment-query dispatcher (a large switch on the
// function id, e.g. cases 0xd3 and 0xfd for f211 / f253). Read-only.
// Arguments: <output_file> <hex case> [<hex case> ...]
// @category ER_Engine
import ghidra.app.script.GhidraScript;
import ghidra.program.model.listing.Function;
import ghidra.program.model.symbol.Namespace;
import ghidra.program.model.symbol.Symbol;
import ghidra.program.model.symbol.SymbolIterator;
import java.io.PrintWriter;
import java.util.*;

public class FindSwitchCases extends GhidraScript {
    @Override
    public void run() throws Exception {
        String[] args = getScriptArgs();
        List<String> want = new ArrayList<>();
        for (int i = 1; i < args.length; ++i) want.add("caseD_" + args[i].toLowerCase());
        Map<Namespace, Set<String>> cases = new HashMap<>();
        Map<Namespace, Integer> counts = new HashMap<>();
        SymbolIterator it = currentProgram.getSymbolTable().getAllSymbols(false);
        while (it.hasNext() && !monitor.isCancelled()) {
            Symbol s = it.next();
            String n = s.getName();
            if (!n.startsWith("caseD_")) continue;
            Namespace ns = s.getParentNamespace();
            if (ns == null || !ns.getName().startsWith("switchD_")) continue;
            counts.merge(ns, 1, Integer::sum);
            if (want.contains(n)) cases.computeIfAbsent(ns, k -> new HashSet<>()).add(n);
        }
        try (PrintWriter w = new PrintWriter(args[0], "UTF-8")) {
            if (want.isEmpty()) {  // no cases given: the 15 largest switches
                List<Map.Entry<Namespace, Integer>> all = new ArrayList<>(counts.entrySet());
                all.sort((x, y) -> y.getValue() - x.getValue());
                w.println(all.size() + " switches");
                for (Map.Entry<Namespace, Integer> e : all.subList(0, Math.min(15, all.size()))) {
                    Namespace fn = e.getKey().getParentNamespace();
                    w.println(e.getKey().getName() + " in " + (fn == null ? "?" : fn.getName()) + ": " + e.getValue() + " cases");
                }
            }
            for (Map.Entry<Namespace, Set<String>> e : cases.entrySet()) {
                if (e.getValue().size() < want.size()) continue;
                Namespace ns = e.getKey();
                Namespace fn = ns.getParentNamespace();
                String fname = fn == null ? "?" : fn.getName();
                Function f = fn instanceof Function ? (Function) fn : null;
                w.println(ns.getName() + " in " + fname + (f != null ? " @" + f.getEntryPoint() : "") + ": "
                    + counts.get(ns) + " cases");
            }
        }
        println("FindSwitchCases done: " + args[0]);
    }
}
