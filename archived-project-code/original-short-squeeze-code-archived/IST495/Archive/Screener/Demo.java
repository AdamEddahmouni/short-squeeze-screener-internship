package Screener;

public class Demo {
    public static void main(String[] args) {
        javax.swing.SwingUtilities.invokeLater(() -> {
            ScreenerModel model = new ScreenerModel();
            ScreenerView view = new ScreenerView();
            //view.combo.setEditable(false);
            new ScreenerController(view, model);
        });
    }
}