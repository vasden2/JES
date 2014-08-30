import sys
import javax.swing as swing
import javax.swing.table.AbstractTableModel as AbstractTableModel
import java.awt as awt
import JESDebugger



def variableDialog(ui):
    var = swing.JOptionPane.showInputDialog(ui, 'Please type the variable to watch')
    return var

class DBControlPanel(swing.JPanel):
    def __init__(self, debugger):
        self.lastValue = None
        self.debugger = debugger
        self.slider = swing.JSlider(swing.JSlider.VERTICAL, 0, 10, self.debugger.speed, stateChanged=self.stateChanged)
        self.stepButton = swing.JButton('step', actionPerformed=self.actionPerformed)  # pic of a boot would be nice
        self.stepButton.setEnabled(0)
        self.setLayout(swing.BoxLayout(self, swing.BoxLayout.Y_AXIS))
        self.add(self.slider)
        self.add(self.stepButton)

    def stateChanged(self, e):
        value = self.slider.getValue()
        if value == 0:
            self.stepButton.setEnabled(1)
            self.debugger.step_mode = 1
        elif self.lastValue == 0:
            self.stepButton.setEnabled(0)
            self.debugger.step_mode = 0
        self.lastValue = value
        self.debugger.setSpeed(value)
        

    def actionPerformed(e):
        debugger.do_step()


class ExecHistory(AbstractTableModel):

    def __init__(self, debugger):
        self.debugger = debugger
        self.variables = []
        self.lines = []

    def fireChanged(self):
        self.fireTableStructureChanged()
        

    def getColumnName(self, col):
        if col == 0:
            return 'line'
        elif col == 1:
            return 'instruction'
        else:
            return self.variables[col - 2]

    def setVariables(self, vars):
        self.variables = vars
        # need to signal the table view here
        self.fireChanged()

    def appendVariable(self, var):
        self.variables.append(var)
        self.fireChanged()

    def clearVariables(self):
        self.variables = []
        self.fireChanged()

    def addLine(self, line_no, instr, values):
        line = []
        line.append(line_no)
        line.append(instr)
        line.extend(values)
        self.lines.append(line)
        self.fireChanged()

    def clear(self):
        self.lines = []
        self.fireChanged()

    def snapShot(self, line_no, instr):
        values = []
        for var in self.variables:
            try:
                value = eval(var, self.debugger.curframe.f_globals,
                             self.debugger.curframe.f_locals)
                values.append(value)
            except:
                values.append('-') # add dummy
                #t, v = sys.exc_info()[:2]
                #if type(t) == type(''):
                    #exc_type_name = t
                #else: exc_type_name = t.__name__
                #print '***', exc_type_name + ':', `v`
        
        self.addLine(line_no, instr, values)
        

    # TableModel required methods
    def getColumnCount(self):
        ret = 2 + len(self.variables)
        return ret

    def getRowCount(self):
        return len(self.lines)

    def getValueAt(self, row, col):
        return self.lines[row][col]

        
class JESDBVariableWatcher(swing.JFrame):

    def __init__(self, debugger):
        swing.JFrame.__init__(self, title='JESDB Variable Watcher')
        # variables correspond to columns on the right
        self.history = ExecHistory(debugger)
        self.controlPanel = DBControlPanel(debugger)
        self.table = swing.JTable(self.history)
        scrollPane = swing.JScrollPane(self.table)
        self.contentPane.setLayout(awt.BorderLayout())
        scrollPane.preferredSize = (200,400)
        self.contentPane.add(scrollPane, awt.BorderLayout.CENTER)
        self.contentPane.add(self.controlPanel, awt.BorderLayout.EAST)
        self.pack()
        #self.show()

    def snapShot(self, line_no, instr):
        self.history.snapShot(line_no, instr)

    def setVariables(self, vars):
        self.history.setVariables(vars)

    def addVariable(self, var):
        self.appendVariable(var)
        

    def appendVariable(self, var):
        self.history.appendVariable(var)

    def clearVariables(self):
        self.history.clearVariables()

    def getVariables(self):
        return self.history.variables

    def clear(self):
        self.history.clear()
