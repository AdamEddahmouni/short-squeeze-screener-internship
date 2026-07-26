package Screener;

import java.io.IOException;
import java.util.HashMap;
import java.util.Map;

public class ScreenerController {
    private ScreenerView view;
    private ScreenerModel model;
    

    public ScreenerController(ScreenerView view, ScreenerModel model) {
        this.view = view;
        this.model = model;

        view.search.addActionListener(e -> {
        model.setTickerSymbol(view.search.getText());
        model.fetchFinvizData(); // Fetch data from Finviz
        Map<String, String> stockData = model.getStockData();
        view.price.setText("Share Price: $" + stockData.get("Price"));
        view.change.setText("Percent Change: " + stockData.get("Change"));
        view.relVol.setText("Relative Volume: "   + stockData.get("Rel Vol"));
        view.floatAmount.setText("Float Amount: " + stockData.get("Float"));
        System.out.println("Ticker set to: " + model.getTickerSymbol());
        });


        /*view.box1.addActionListener(e -> handleCheckboxChange(1, view.box1.isSelected()));
        view.box2.addActionListener(e -> handleCheckboxChange(2, view.box2.isSelected()));
        view.box3.addActionListener(e -> handleCheckboxChange(3, view.box3.isSelected()));
        view.box4.addActionListener(e -> handleCheckboxChange(4, view.box4.isSelected()));
        view.box5.addActionListener(e -> handleCheckboxChange(5, view.box5.isSelected()));*/
    }

    /*private void handleCheckboxChange(int index, boolean state) {
        model.setCheckboxState(index, state);
        model.setLikelihood();
        String likelihood = model.getSelectedLikelihood();
        view.combo.setSelectedItem(likelihood);
        System.out.println("Likelihood updated: " + likelihood);
    }*/

    
}