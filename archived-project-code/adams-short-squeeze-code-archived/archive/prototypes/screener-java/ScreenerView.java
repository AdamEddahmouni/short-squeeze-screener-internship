package Screener;

import javax.swing.*;
import java.awt.*;

public class ScreenerView extends JFrame {
    public JTextField search = new JTextField();
    /*public JCheckBox box1 = new JCheckBox("Price between $2 and $20");
    public JCheckBox box2 = new JCheckBox("Up 10% on day");
    public JCheckBox box3 = new JCheckBox("Relative Volume");
    
    public JCheckBox box5 = new JCheckBox("20M Float");
    public JComboBox<String> combo = new JComboBox<>();*/
    public JCheckBox box4 = new JCheckBox("News Catalyst");
    public JLabel price = new JLabel("Price:");
    public JLabel change = new JLabel("Percent Change:");
    public JLabel relVol = new JLabel("Relative Voume:");
    public JLabel floatAmount = new JLabel("Float:");

    public ScreenerView(){
    
        JFrame frame = new JFrame("Screener");
        frame.setSize(800, 500);
        frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);

        frame.setLayout(new GridBagLayout());
        GridBagConstraints g = new GridBagConstraints();
        
        JLabel label = new JLabel("Ticker Symbol ID");
        g.gridx = 2;
        g.gridy = 0;
        frame.add(label, g);

        
        g.gridx = 2;
        g.gridy = 1;
        g.gridwidth = 2;
        g.fill = GridBagConstraints.HORIZONTAL;
        frame.add(search, g);

       
        g.gridx = 0;
        g.gridy = 2;
        frame.add(price, g);

        
        g.gridx = 0;
        g.gridy = 3;
        frame.add(change, g);

        
        g.gridx = 0;
        g.gridy = 4;
        frame.add(relVol, g);

        
        g.gridx = 3;
        g.gridy = 2;
        frame.add(floatAmount, g);

        
        g.gridx = 3;
        g.gridy = 3;
        frame.add(box4, g);

        
        /*combo.addItem("High Likelyhood");
        combo.addItem("Medium Likelyhood");
        combo.addItem("Low Likelyhood");
        combo.setSelectedItem("Low Likelyhood");
        combo.setEditable(false);
        g.gridx = 3;
        g.gridy = 4;
        g.anchor = GridBagConstraints.WEST;
        frame.add(combo, g);*/

        frame.setVisible(true);
    }
}
